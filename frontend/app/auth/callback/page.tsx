'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { consumeMagicLink } from '@/lib/api';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setStatus('error');
      setMessage('No token provided');
      return;
    }

    consumeMagicLink(token)
      .then(() => {
        setStatus('success');
        setTimeout(() => {
          router.push('/dashboard');
        }, 1000);
      })
      .catch((error: any) => {
        setStatus('error');
        setMessage(error.message || 'Invalid or expired token');
      });
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow text-center">
        {status === 'loading' && (
          <div>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Verifying token...</p>
          </div>
        )}
        {status === 'success' && (
          <div>
            <div className="text-green-600 text-4xl mb-4">✓</div>
            <p className="text-gray-900 font-medium">Login successful!</p>
            <p className="text-gray-600">Redirecting to dashboard...</p>
          </div>
        )}
        {status === 'error' && (
          <div>
            <div className="text-red-600 text-4xl mb-4">✗</div>
            <p className="text-gray-900 font-medium">Login failed</p>
            <p className="text-gray-600">{message}</p>
            <button
              onClick={() => router.push('/login')}
              className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Back to Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
