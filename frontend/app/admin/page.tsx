import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import { getCurrentUser } from '@/lib/api';
import AdminClient from './AdminClient';

export default async function AdminPage() {
  const cookieStore = await cookies();
  const session = cookieStore.get('efi_session');
  
  if (!session) {
    redirect('/login');
  }

  try {
    const user = await getCurrentUser();
    if (user.role !== 'admin') {
      redirect('/dashboard');
    }

    return <AdminClient user={user} />;
  } catch {
    redirect('/login');
  }
}
