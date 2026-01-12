'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  adminGetExchanges,
  adminCreateExchange,
  adminGetAddresses,
  adminCreateAddress,
  adminGetSyncState,
  adminTriggerResync,
} from '@/lib/api';

interface AdminClientProps {
  user: any;
}

export default function AdminClient({ user }: AdminClientProps) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'exchanges' | 'addresses' | 'sync'>('exchanges');
  const [exchanges, setExchanges] = useState<any[]>([]);
  const [addresses, setAddresses] = useState<any[]>([]);
  const [syncState, setSyncState] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load exchanges first (needed for addresses form)
    adminGetExchanges().then(setExchanges).catch(console.error);
  }, []);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'exchanges') {
        const data = await adminGetExchanges();
        setExchanges(data);
      } else if (activeTab === 'addresses') {
        const data = await adminGetAddresses();
        setAddresses(data);
        // Also refresh exchanges for the form
        const exData = await adminGetExchanges();
        setExchanges(exData);
      } else if (activeTab === 'sync') {
        const data = await adminGetSyncState();
        setSyncState(data);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateExchange = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const name = formData.get('name') as string;
    const slug = formData.get('slug') as string;

    try {
      await adminCreateExchange({ name, slug });
      loadData();
      (e.target as HTMLFormElement).reset();
    } catch (error: any) {
      alert(error.message || 'Failed to create exchange');
    }
  };

  const handleCreateAddress = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const data = {
      exchange_id: formData.get('exchange_id') as string,
      chain: formData.get('chain') as string,
      address: formData.get('address') as string,
      label: formData.get('label') as string,
      is_active: formData.get('is_active') === 'on',
    };

    try {
      await adminCreateAddress(data);
      loadData();
      (e.target as HTMLFormElement).reset();
    } catch (error: any) {
      alert(error.message || 'Failed to create address');
    }
  };

  const handleResync = async () => {
    if (!confirm('Trigger resync? This will enqueue ingestion jobs.')) return;
    try {
      await adminTriggerResync();
      alert('Resync triggered');
    } catch (error: any) {
      alert(error.message || 'Failed to trigger resync');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Admin Panel</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('exchanges')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'exchanges'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Exchanges
              </button>
              <button
                onClick={() => setActiveTab('addresses')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'addresses'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Addresses
              </button>
              <button
                onClick={() => setActiveTab('sync')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'sync'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Sync State
              </button>
            </nav>
          </div>

          {/* Exchanges Tab */}
          {activeTab === 'exchanges' && (
            <div>
              <h2 className="text-xl font-bold mb-4">Exchanges</h2>
              
              {/* Create Form */}
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h3 className="text-lg font-semibold mb-4">Create Exchange</h3>
                <form onSubmit={handleCreateExchange} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Name</label>
                    <input
                      type="text"
                      name="name"
                      required
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Slug</label>
                    <input
                      type="text"
                      name="slug"
                      required
                      pattern="[a-z0-9-]+"
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    Create
                  </button>
                </form>
              </div>

              {/* List */}
              {loading ? (
                <div className="text-center py-8">Loading...</div>
              ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Slug</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {exchanges.map((ex) => (
                        <tr key={ex.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{ex.name}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{ex.slug}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(ex.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Addresses Tab */}
          {activeTab === 'addresses' && (
            <div>
              <h2 className="text-xl font-bold mb-4">Addresses</h2>
              
              {/* Create Form */}
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h3 className="text-lg font-semibold mb-4">Add Address</h3>
                <form onSubmit={handleCreateAddress} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Exchange</label>
                    <select name="exchange_id" required className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="">Select exchange</option>
                      {exchanges.map((ex) => (
                        <option key={ex.id} value={ex.id}>{ex.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Chain</label>
                    <select name="chain" required className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="EVM">EVM</option>
                      <option value="BTC">BTC</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Address</label>
                    <input
                      type="text"
                      name="address"
                      required
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Label</label>
                    <select name="label" required className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="hot">Hot</option>
                      <option value="cold">Cold</option>
                      <option value="deposit">Deposit</option>
                      <option value="reserve">Reserve</option>
                    </select>
                  </div>
                  <div className="flex items-center">
                    <input type="checkbox" name="is_active" defaultChecked className="mr-2" />
                    <label className="text-sm text-gray-700">Active</label>
                  </div>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    Add Address
                  </button>
                </form>
              </div>

              {/* List */}
              {loading ? (
                <div className="text-center py-8">Loading...</div>
              ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exchange</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chain</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Address</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Label</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Active</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {addresses.map((addr) => (
                        <tr key={addr.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">{addr.exchange_id}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">{addr.chain}</td>
                          <td className="px-6 py-4 text-sm font-mono">{addr.address}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">{addr.label}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">{addr.is_active ? 'Yes' : 'No'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Sync State Tab */}
          {activeTab === 'sync' && (
            <div>
              <h2 className="text-xl font-bold mb-4">Sync State</h2>
              
              <div className="mb-4">
                <button
                  onClick={handleResync}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                >
                  Trigger Resync
                </button>
              </div>

              {loading ? (
                <div className="text-center py-8">Loading...</div>
              ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chain</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Block</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Height</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {syncState.map((state) => (
                        <tr key={state.chain}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{state.chain}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">{state.last_processed_block || '-'}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">{state.last_processed_height || '-'}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(state.updated_at).toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
