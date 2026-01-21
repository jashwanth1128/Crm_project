import React, { useState, useEffect } from 'react';
import { Layout } from '../components/layout/Layout';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Plus, Phone, Mail, MessageSquare, FileText, CheckSquare, Clock } from 'lucide-react';
import { api } from '../utils/api';
import { toast } from 'sonner';
import { Badge } from '../components/ui/badge';

const ACTIVITY_TYPES = [
  { value: 'CALL', label: 'Call', icon: Phone, color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' },
  { value: 'EMAIL', label: 'Email', icon: Mail, color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300' },
  { value: 'MEETING', label: 'Meeting', icon: MessageSquare, color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' },
  { value: 'NOTE', label: 'Note', icon: FileText, color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' },
  { value: 'TASK', label: 'Task', icon: CheckSquare, color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300' }
];

export default function ActivitiesPage() {
  const [activities, setActivities] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [leads, setLeads] = useState([]);
  const [users, setUsers] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    type: 'NOTE',
    subject: '',
    description: '',
    duration: '',
    customer_id: '',
    lead_id: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [activitiesRes, customersRes, leadsRes, usersRes] = await Promise.all([
        api.getActivities({ limit: 100 }),
        api.getCustomers({ limit: 1000 }),
        api.getLeads({ limit: 1000 }),
        api.getUsers()
      ]);
      setActivities(activitiesRes.data);
      setCustomers(customersRes.data);
      setLeads(leadsRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      toast.error('Failed to load activities');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        duration: formData.duration ? parseInt(formData.duration) : null,
        customer_id: formData.customer_id || null,
        lead_id: formData.lead_id || null
      };
      await api.createActivity(data);
      toast.success('Activity created successfully');
      setIsDialogOpen(false);
      setFormData({
        type: 'NOTE',
        subject: '',
        description: '',
        duration: '',
        customer_id: '',
        lead_id: ''
      });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create activity');
    }
  };

  const getActivityTypeInfo = (type) => {
    return ACTIVITY_TYPES.find(t => t.value === type) || ACTIVITY_TYPES[3];
  };

  return (
    <Layout>
      <div data-testid="activities-page">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Activities</h1>
            <p className="text-muted-foreground mt-2">Track all customer interactions</p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button data-testid="create-activity-btn">
                <Plus className="w-4 h-4 mr-2" />
                New Activity
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Create New Activity</DialogTitle>
                <DialogDescription>Log a new customer interaction</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="type">Type *</Label>
                    <Select
                      value={formData.type}
                      onValueChange={(value) => setFormData({ ...formData, type: value })}
                    >
                      <SelectTrigger data-testid="activity-type-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {ACTIVITY_TYPES.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="subject">Subject *</Label>
                    <Input
                      id="subject"
                      data-testid="activity-subject-input"
                      value={formData.subject}
                      onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      data-testid="activity-description-input"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={3}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="duration">Duration (minutes)</Label>
                    <Input
                      id="duration"
                      data-testid="activity-duration-input"
                      type="number"
                      value={formData.duration}
                      onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="customer">Customer</Label>
                    <Select
                      value={formData.customer_id}
                      onValueChange={(value) => setFormData({ ...formData, customer_id: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="None" />
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
                    <Label htmlFor="lead">Lead</Label>
                    <Select
                      value={formData.lead_id}
                      onValueChange={(value) => setFormData({ ...formData, lead_id: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="None" />
                      </SelectTrigger>
                      <SelectContent>
                        {leads.map((lead) => (
                          <SelectItem key={lead.id} value={lead.id}>
                            {lead.title}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" data-testid="submit-activity-btn">Create Activity</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="max-w-4xl">
            <div className="relative">
              <div className="absolute left-6 top-0 bottom-0 w-px bg-border" />
              <div className="space-y-6">
                {activities.map((activity) => {
                  const typeInfo = getActivityTypeInfo(activity.type);
                  const Icon = typeInfo.icon;
                  const customer = customers.find(c => c.id === activity.customer_id);
                  const lead = leads.find(l => l.id === activity.lead_id);
                  const user = users.find(u => u.id === activity.user_id);

                  return (
                    <div key={activity.id} className="relative pl-14" data-testid={`activity-item-${activity.id}`}>
                      <div className="absolute left-0 w-12 h-12 rounded-full bg-card border-2 border-border flex items-center justify-center">
                        <Icon className="w-5 h-5" />
                      </div>
                      <Card>
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <div>
                              <CardTitle className="text-base">{activity.subject}</CardTitle>
                              <CardDescription className="flex items-center space-x-2 mt-1">
                                <Badge className={typeInfo.color}>{typeInfo.label}</Badge>
                                {activity.duration && (
                                  <span className="flex items-center text-xs">
                                    <Clock className="w-3 h-3 mr-1" />
                                    {activity.duration}m
                                  </span>
                                )}
                              </CardDescription>
                            </div>
                            <span className="text-xs text-muted-foreground">
                              {new Date(activity.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </CardHeader>
                        <CardContent>
                          {activity.description && (
                            <p className="text-sm text-muted-foreground mb-3">{activity.description}</p>
                          )}
                          <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                            {user && <span>By: {user.first_name} {user.last_name}</span>}
                            {customer && <span>• Customer: {customer.name}</span>}
                            {lead && <span>• Lead: {lead.title}</span>}
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
