import * as Icons from 'lucide-react';

interface LucideIconProps {
    name: string;
    className?: string;
}

export const LucideIcon = ({ name, className }: LucideIconProps) => {
    const Icon = (Icons as any)[name];

    if (!Icon) {
        return <Icons.HelpCircle className={className} />;
    }

    return <Icon className={className} />;
};
