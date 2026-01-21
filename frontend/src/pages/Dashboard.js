import React, { useState, useEffect } from 'react';
import { Layout } from '../components/layout/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Users, Target, TrendingUp, Activity as ActivityIcon, DollarSign } from 'lucide-react';
import { api } from '../utils/api';
import { toast } from 'sonner';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalCustomers: 0,
    totalLeads: 0,
    totalActivities: 0,
    conversionRate: 0,
    totalValue: 0
  });
  const [leadsByStatus, setLeadsByStatus] = useState([]);
  const [recentActivities, setRecentActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [customersRes, leadsRes, activitiesRes, statsRes] = await Promise.all([
        api.getCustomers({ limit: 1000 }),
        api.getLeads({ limit: 1000 }),
        api.getActivities({ limit: 10 }),
        api.getLeadStats()
      ]);

      const customers = customersRes.data;
      const leads = leadsRes.data;
      const activities = activitiesRes.data;

      const convertedLeads = leads.filter(l => l.status === 'CONVERTED').length;
      const conversionRate = leads.length > 0 ? ((convertedLeads / leads.length) * 100).toFixed(1) : 0;
      const totalValue = leads.reduce((sum, lead) => sum + (lead.value || 0), 0);

      setStats({
        totalCustomers: customers.length,
        totalLeads: leads.length,
        totalActivities: activities.length,
        conversionRate,
        totalValue
      });

      // Group leads by status
      const statusCounts = {};
      leads.forEach(lead => {
        statusCounts[lead.status] = (statusCounts[lead.status] || 0) + 1;
      });
      setLeadsByStatus(Object.entries(statusCounts).map(([status, count]) => ({ status, count })));

      setRecentActivities(activities);
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Customers',
      value: stats.totalCustomers,
      icon: Users,
      description: 'Active customers',
      color: 'text-blue-600'
    },
    {
      title: 'Total Leads',
      value: stats.totalLeads,
      icon: Target,
      description: 'In pipeline',
      color: 'text-purple-600'
    },
    {
      title: 'Conversion Rate',
      value: `${stats.conversionRate}%`,
      icon: TrendingUp,
      description: 'Lead to customer',
      color: 'text-green-600'
    },
    {
      title: 'Total Value',
      value: `$${stats.totalValue.toLocaleString()}`,
      icon: DollarSign,
      description: 'Pipeline value',
      color: 'text-yellow-600'
    }
  ];

  return (
    <Layout>
      <div data-testid="dashboard-page">
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-2">Overview of your CRM metrics</p>
        </div>

        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {statCards.map((stat) => {
                const Icon = stat.icon;
                return (
                  <Card key={stat.title} data-testid={`stat-card-${stat.title.toLowerCase().replace(/\s+/g, '-')}`}>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        {stat.title}
                      </CardTitle>
                      <Icon className={`w-5 h-5 ${stat.color}`} />
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-bold">{stat.value}</div>
                      <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <Card data-testid="leads-by-status-card">
                <CardHeader>
                  <CardTitle>Leads by Status</CardTitle>
                  <CardDescription>Distribution across pipeline stages</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {leadsByStatus.map(({ status, count }) => (
                      <div key={status} className="flex items-center justify-between">
                        <span className="text-sm font-medium">{status}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-32 h-2 bg-secondary rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary rounded-full"
                              style={{ width: `${(count / stats.totalLeads) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm text-muted-foreground w-8 text-right">{count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card data-testid="recent-activities-card">
                <CardHeader>
                  <CardTitle>Recent Activities</CardTitle>
                  <CardDescription>Latest team activities</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {recentActivities.length === 0 ? (
                      <p className="text-sm text-muted-foreground text-center py-4">No activities yet</p>
                    ) : (
                      recentActivities.map((activity) => (
                        <div key={activity.id} className="flex items-start space-x-3">
                          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                            <ActivityIcon className="w-4 h-4" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{activity.subject}</p>
                            <p className="text-xs text-muted-foreground">
                              {activity.type} • {new Date(activity.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}
