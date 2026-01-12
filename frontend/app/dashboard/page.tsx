import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import { getCurrentUser, getExchanges, getLiveAlerts } from '@/lib/api';
import DashboardClient from './DashboardClient';

export default async function DashboardPage() {
  const cookieStore = await cookies();
  const session = cookieStore.get('efi_session');
  
  if (!session) {
    redirect('/login');
  }

  try {
    const user = await getCurrentUser();
    const exchanges = await getExchanges();
    const alerts = await getLiveAlerts();

    return <DashboardClient user={user} exchanges={exchanges} alerts={alerts} />;
  } catch {
    redirect('/login');
  }
}
