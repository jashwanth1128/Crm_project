import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '../../lib/utils';
import { Building2, LayoutDashboard, Users, Target, Activity, Settings, LogOut, FileText } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/button';
import { Separator } from '../ui/separator';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { ScrollArea } from '../ui/scroll-area';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Deals', href: '/deals', icon: Building2 },
  { name: 'Accounts', href: '/accounts', icon: Users },
  { name: 'Leads', href: '/leads', icon: Target },
  { name: 'Activities', href: '/activities', icon: Activity },
];

const adminNavigation = [
  { name: 'Users', href: '/users', icon: Users },
  { name: 'Audit Logs', href: '/audit-logs', icon: FileText },
];

export const Sidebar = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const getInitials = () => {
    if (!user) return 'U';
    return `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`;
  };

  return (
    <div className="flex h-screen w-64 flex-col fixed left-0 top-0 border-r bg-card/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60" data-testid="sidebar">
      <div className="p-6">
        <Link to="/dashboard" className="flex items-center space-x-3 group">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/30 transition-transform group-hover:scale-105">
            <Building2 className="w-6 h-6" />
          </div>
          <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-indigo-600">CRM Pro</span>
        </Link>
      </div>

      <Separator className="bg-border/50" />

      <ScrollArea className="flex-1 py-4">
        <nav className="px-4 space-y-2">
          <div className="px-2 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Menu
          </div>
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                data-testid={`nav-${item.name.toLowerCase()}`}
                className={cn(
                  'flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group relative overflow-hidden',
                  isActive
                    ? 'text-primary-foreground shadow-md'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                )}
              >
                {isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 z-0"></div>
                )}
                <Icon className={cn("w-5 h-5 z-10 relative", isActive ? "text-white" : "")} />
                <span className={cn("z-10 relative", isActive ? "text-white" : "")}>{item.name}</span>
              </Link>
            );
          })}

          {user?.role === 'ADMIN' && (
            <>
              <div className="px-2 py-2 mt-6 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Admin
              </div>
              {adminNavigation.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    data-testid={`nav-${item.name.toLowerCase()}`}
                    className={cn(
                      'flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group relative overflow-hidden',
                      isActive
                        ? 'text-primary-foreground shadow-md'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                    )}
                  >
                    {isActive && (
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 z-0"></div>
                    )}
                    <Icon className={cn("w-5 h-5 z-10 relative", isActive ? "text-white" : "")} />
                    <span className={cn("z-10 relative", isActive ? "text-white" : "")}>{item.name}</span>
                  </Link>
                );
              })}
            </>
          )}
        </nav>
      </ScrollArea>

      <Separator className="bg-border/50" />

      <div className="p-4 space-y-2 bg-muted/20">
        <Link
          to="/settings"
          data-testid="nav-settings"
          className={cn(
            'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200',
            location.pathname === '/settings'
              ? 'bg-secondary text-secondary-foreground'
              : 'text-muted-foreground hover:text-foreground hover:bg-muted'
          )}
        >
          <Settings className="w-5 h-5" />
          <span>Settings</span>
        </Link>

        <div className="flex items-center space-x-3 px-3 py-2 bg-gradient-to-br from-card to-secondary/10 rounded-xl border border-border/50 shadow-sm mt-2">
          <Avatar className="w-9 h-9 border-2 border-background">
            <AvatarImage src={user?.avatar} />
            <AvatarFallback className="bg-primary/10 text-primary">{getInitials()}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate">{user?.first_name} {user?.last_name}</p>
            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
          </div>
        </div>

        <Button
          variant="ghost"
          className="w-full justify-start text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20"
          onClick={logout}
          data-testid="logout-btn"
        >
          <LogOut className="w-5 h-5 mr-3" />
          Logout
        </Button>
      </div>
    </div>
  );
};
