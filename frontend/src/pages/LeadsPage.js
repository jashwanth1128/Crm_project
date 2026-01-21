import React, { useState, useEffect } from 'react';
import { Layout } from '../components/layout/Layout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Plus, LayoutGrid, List, DollarSign } from 'lucide-react';
import { api } from '../utils/api';
import { toast } from 'sonner';
import { Badge } from '../components/ui/badge';
import { cn } from '../lib/utils';

const LEAD_STATUSES = [
  { value: 'NEW', label: 'New', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' },
  { value: 'CONTACTED', label: 'Contacted', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300' },
  { value: 'QUALIFIED', label: 'Qualified', color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300' },
  { value: 'PROPOSAL', label: 'Proposal', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' },
  { value: 'NEGOTIATION', label: 'Negotiation', color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300' },
  { value: 'CONVERTED', label: 'Converted', color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' },
  { value: 'LOST', label: 'Lost', color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' }
];

export default function LeadsPage() {
  const [leads, setLeads] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [users, setUsers] = useState([]);
  const [viewMode, setViewMode] = useState('kanban');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    value: '',
    status: 'NEW',
    source: 'OTHER',
    customer_id: '',
    assigned_to: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [leadsRes, customersRes, usersRes] = await Promise.all([
        api.getLeads({ limit: 1000 }),
        api.getCustomers({ limit: 1000 }),
        api.getUsers()
      ]);
      setLeads(leadsRes.data);
      setCustomers(customersRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      toast.error('Failed to load leads');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        value: formData.value ? parseFloat(formData.value) : null,
        assigned_to: formData.assigned_to || null
      };
      await api.createLead(data);
      toast.success('Lead created successfully');
      setIsDialogOpen(false);
      setFormData({
        title: '',
        description: '',
        value: '',
        status: 'NEW',
        source: 'OTHER',
        customer_id: '',
        assigned_to: ''
      });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create lead');
    }
  };

  const handleUpdateStatus = async (leadId, newStatus) => {
    try {
      await api.updateLead(leadId, { status: newStatus });
      toast.success('Lead status updated');
      fetchData();
    } catch (error) {
      toast.error('Failed to update lead status');
    }
  };

  const LeadCard = ({ lead }) => {
    const customer = customers.find(c => c.id === lead.customer_id);
    const statusInfo = LEAD_STATUSES.find(s => s.value === lead.status);

    return (
      <Card className="mb-3 hover:border-primary/20 transition-colors duration-200" data-testid={`lead-card-${lead.id}`}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <CardTitle className="text-base">{lead.title}</CardTitle>
            {lead.value && (
              <Badge variant="outline" className="ml-2 flex items-center space-x-1">
                <DollarSign className="w-3 h-3" />
                <span>{lead.value.toLocaleString()}</span>
              </Badge>
            )}
          </div>
          {customer && (
            <CardDescription className="text-xs">{customer.name}</CardDescription>
          )}
        </CardHeader>
        <CardContent>
          {lead.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-2">{lead.description}</p>
          )}
          <div className="flex items-center justify-between mt-2">
            <Badge className={cn('text-xs', statusInfo?.color)}>
              {statusInfo?.label}
            </Badge>
            <span className="text-xs text-muted-foreground">
              {new Date(lead.created_at).toLocaleDateString()}
            </span>
          </div>
        </CardContent>
      </Card>
    );
  };

  const KanbanView = () => (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4" data-testid="kanban-view">
      {LEAD_STATUSES.map((status) => {
        const statusLeads = leads.filter(lead => lead.status === status.value);
        return (
          <div key={status.value} className="flex flex-col">
            <div className="mb-3 p-3 bg-card rounded-md border">
              <h3 className="text-sm font-semibold flex items-center justify-between">
                {status.label}
                <Badge variant="secondary" className="ml-2">{statusLeads.length}</Badge>
              </h3>
            </div>
            <div className="flex-1 space-y-2">
              {statusLeads.map(lead => (
                <LeadCard key={lead.id} lead={lead} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );

  const ListView = () => (
    <div className="space-y-3" data-testid="list-view">
      {leads.map(lead => (
        <LeadCard key={lead.id} lead={lead} />
      ))}
    </div>
  );

  return (
    <Layout>
      <div data-testid="leads-page">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Leads</h1>
            <p className="text-muted-foreground mt-2">Manage your sales pipeline</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center border rounded-md">
              <Button
                variant={viewMode === 'kanban' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('kanban')}
                data-testid="kanban-view-btn"
              >
                <LayoutGrid className="w-4 h-4 mr-2" />
                Kanban
              </Button>
              <Button
                variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('list')}
                data-testid="list-view-btn"
              >
                <List className="w-4 h-4 mr-2" />
                List
              </Button>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button data-testid="create-lead-btn">
                  <Plus className="w-4 h-4 mr-2" />
                  New Lead
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Create New Lead</DialogTitle>
                  <DialogDescription>Add a new lead to your pipeline</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit}>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="title">Title *</Label>
                      <Input
                        id="title"
                        data-testid="lead-title-input"
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="customer">Customer *</Label>
                      <Select
                        value={formData.customer_id}
                        onValueChange={(value) => setFormData({ ...formData, customer_id: value })}
                        required
                      >
                        <SelectTrigger data-testid="lead-customer-select">
                          <SelectValue placeholder="Select customer" />
                        </SelectTrigger>
                        <SelectContent>
                          {customers.map((customer) => (
                            <SelectItem key={customer.id} value={customer.id}>
                              {customer.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="description">Description</Label>
                      <Textarea
                        id="description"
                        data-testid="lead-description-input"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        rows={3}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="value">Value ($)</Label>
                      <Input
                        id="value"
                        data-testid="lead-value-input"
                        type="number"
                        step="0.01"
                        value={formData.value}
                        onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="source">Source</Label>
                        <Select
                          value={formData.source}
                          onValueChange={(value) => setFormData({ ...formData, source: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="WEBSITE">Website</SelectItem>
                            <SelectItem value="REFERRAL">Referral</SelectItem>
                            <SelectItem value="COLD_CALL">Cold Call</SelectItem>
                            <SelectItem value="EMAIL">Email</SelectItem>
                            <SelectItem value="SOCIAL_MEDIA">Social Media</SelectItem>
                            <SelectItem value="OTHER">Other</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="assigned_to">Assign To</Label>
                        <Select
                          value={formData.assigned_to}
                          onValueChange={(value) => setFormData({ ...formData, assigned_to: value })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Unassigned" />
                          </SelectTrigger>
                          <SelectContent>
                            {users.map((user) => (
                              <SelectItem key={user.id} value={user.id}>
                                {user.first_name} {user.last_name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" data-testid="submit-lead-btn">Create Lead</Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          viewMode === 'kanban' ? <KanbanView /> : <ListView />
        )}
      </div>
    </Layout>
  );
}
