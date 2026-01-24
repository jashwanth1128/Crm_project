import React from 'react';
import { Layout } from '../components/layout/Layout';
import { DealsKanban } from '../components/deals/DealsKanban';
import { Button } from '../components/ui/button';
import { Plus } from 'lucide-react';

export default function DealsPage() {
    return (
        <Layout>
            <div className="flex flex-col h-[calc(100vh-8rem)]">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Deals Pipeline</h1>
                        <p className="text-muted-foreground">Manage your opportunities and revenue.</p>
                    </div>
                    <Button>
                        <Plus className="w-4 h-4 mr-2" />
                        New Deal
                    </Button>
                </div>
                <div className="flex-1 overflow-x-auto">
                    <DealsKanban />
                </div>
            </div>
        </Layout>
    );
}
