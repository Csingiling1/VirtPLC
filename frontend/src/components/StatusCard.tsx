import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { LucideIcon } from 'lucide-react';
import { cn } from '../utils';

interface StatusCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  status?: 'success' | 'warning' | 'danger' | 'info';
  subtitle?: string;
}

const StatusCard = ({ title, value, icon: Icon, status = 'info', subtitle }: StatusCardProps) => {
  const statusColors = {
    success: 'text-status-success',
    warning: 'text-status-warning',
    danger: 'text-status-danger',
    info: 'text-primary',
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className={cn('h-5 w-5', statusColors[status])} />
      </CardHeader>
      <CardContent>
        <div className={cn('text-2xl font-bold', statusColors[status])}>
          {value}
        </div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">
            {subtitle}
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export default StatusCard;
