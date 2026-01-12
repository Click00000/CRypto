import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import { getCurrentUser } from '@/lib/api';

export default async function Home() {
  const cookieStore = await cookies();
  const session = cookieStore.get('efi_session');
  
  if (!session) {
    redirect('/login');
  }
  
  try {
    await getCurrentUser();
    redirect('/dashboard');
  } catch {
    redirect('/login');
  }
}
