import { forwardRef } from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', type = 'text', ...props }, ref) => (
    <input
      type={type}
      ref={ref}
      className={`flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-1 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    />
  )
);
Input.displayName = 'Input';
export { Input };
