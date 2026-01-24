import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { api } from '../utils/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { toast } from 'sonner';

// To be fetched from DB/Constants ideally
const STAGES = {
    QUALIFICATION: 'Qualification',
    NEEDS_ANALYSIS: 'Needs Analysis',
    PROPOSAL: 'Proposal',
    NEGOTIATION: 'Negotiation',
    CLOSED_WON: 'Closed Won',
    CLOSED_LOST: 'Closed Lost'
};

const STAGE_COLORS = {
    QUALIFICATION: 'bg-blue-100 text-blue-800',
    NEEDS_ANALYSIS: 'bg-indigo-100 text-indigo-800',
    PROPOSAL: 'bg-yellow-100 text-yellow-800',
    NEGOTIATION: 'bg-orange-100 text-orange-800',
    CLOSED_WON: 'bg-green-100 text-green-800',
    CLOSED_LOST: 'bg-red-100 text-red-800'
};

export function DealsKanban() {
    const [columns, setColumns] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDeals();
    }, []);

    const fetchDeals = async () => {
        try {
            const response = await api.getDeals();
            const deals = response.data;

            const newColumns = Object.keys(STAGES).reduce((acc, stage) => {
                acc[stage] = {
                    name: STAGES[stage],
                    items: deals.filter(d => d.stage === stage)
                };
                return acc;
            }, {});

            setColumns(newColumns);
        } catch (error) {
            toast.error('Failed to load deals');
        } finally {
            setLoading(false);
        }
    };

    const onDragEnd = async (result, columns, setColumns) => {
        if (!result.destination) return;
        const { source, destination } = result;

        if (source.droppableId !== destination.droppableId) {
            const sourceColumn = columns[source.droppableId];
            const destColumn = columns[destination.droppableId];
            const sourceItems = [...sourceColumn.items];
            const destItems = [...destColumn.items];
            const [removed] = sourceItems.splice(source.index, 1);

            // Update local state optimistic
            destItems.splice(destination.index, 0, removed);
            setColumns({
                ...columns,
                [source.droppableId]: { ...sourceColumn, items: sourceItems },
                [destination.droppableId]: { ...destColumn, items: destItems }
            });

            // API Call
            try {
                const newStage = destination.droppableId;
                // Update deal stage
                await api.updateDeal(removed.id, { stage: newStage });
                toast.success(`Deal moved to ${STAGES[newStage]}`);
            } catch (error) {
                toast.error("Failed to update deal stage");
                fetchDeals(); // Revert on error
            }
        } else {
            const column = columns[source.droppableId];
            const copiedItems = [...column.items];
            const [removed] = copiedItems.splice(source.index, 1);
            copiedItems.splice(destination.index, 0, removed);
            setColumns({
                ...columns,
                [source.droppableId]: { ...column, items: copiedItems }
            });
        }
    };

    if (loading) return <div>Loading pipeline...</div>;

    return (
        <div className="flex h-full overflow-x-auto pb-4 gap-4">
            <DragDropContext onDragEnd={result => onDragEnd(result, columns, setColumns)}>
                {Object.entries(columns).map(([columnId, column], index) => {
                    return (
                        <div
                            key={columnId}
                            className="flex flex-col min-w-[300px] w-[300px] bg-secondary/30 rounded-xl p-2"
                        >
                            <div className="p-3 font-semibold text-sm flex justify-between items-center text-muted-foreground uppercase tracking-wider">
                                {column.name}
                                <Badge variant="outline" className="bg-background">{column.items.length}</Badge>
                            </div>
                            <Droppable droppableId={columnId} key={columnId}>
                                {(provided, snapshot) => (
                                    <div
                                        {...provided.droppableProps}
                                        ref={provided.innerRef}
                                        className={`flex-1 space-y-3 p-2 rounded-lg transition-colors ${snapshot.isDraggingOver ? 'bg-primary/5' : ''
                                            }`}
                                    >
                                        {column.items.map((item, index) => {
                                            return (
                                                <Draggable key={item.id} draggableId={item.id} index={index}>
                                                    {(provided, snapshot) => (
                                                        <div
                                                            ref={provided.innerRef}
                                                            {...provided.draggableProps}
                                                            {...provided.dragHandleProps}
                                                            style={{ ...provided.draggableProps.style }}
                                                        >
                                                            <Card className={`shadow-sm hover:shadow-md transition-shadow border-none ${snapshot.isDragging ? 'shadow-xl ring-2 ring-primary rotate-2' : ''}`}>
                                                                <CardContent className="p-4 space-y-2">
                                                                    <div className="font-semibold text-sm line-clamp-2">{item.title}</div>
                                                                    <div className="flex justify-between items-center text-xs text-muted-foreground">
                                                                        <span>${item.value?.toLocaleString()}</span>
                                                                        <span>{new Date(item.created_at).toLocaleDateString()}</span>
                                                                    </div>
                                                                </CardContent>
                                                            </Card>
                                                        </div>
                                                    )}
                                                </Draggable>
                                            );
                                        })}
                                        {provided.placeholder}
                                    </div>
                                )}
                            </Droppable>
                        </div>
                    );
                })}
            </DragDropContext>
        </div>
    );
}
