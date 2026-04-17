import React, { useEffect, useState } from 'react';
import { getDeveloperInfo } from '../services/developerService';

const DeveloperPage = () => {
  const [developerInfo, setDeveloperInfo] = useState(null);

  useEffect(() => {
    const loadDeveloperInfo = async () => {
      try {
        const data = await getDeveloperInfo();
        setDeveloperInfo(data);
      } catch (error) {
        console.error('Error fetching developer info:', error);
      }
    };

    loadDeveloperInfo();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto max-w-4xl px-4 py-10">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Developer Page</p>
            <h1 className="mt-2 text-4xl font-bold text-slate-900">Developer Information</h1>
          </div>
          <a
            href="/"
            className="inline-flex items-center rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-100"
          >
            Back To Dashboard
          </a>
        </div>

        {!developerInfo ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <p className="text-slate-600">Loading developer information...</p>
          </div>
        ) : (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Developer</p>
                <h2 className="mt-2 text-3xl font-semibold text-slate-900">{developerInfo.name}</h2>
                <p className="mt-3 text-sm text-slate-600">{developerInfo.rights}</p>
              </div>
              <div className="grid gap-4">
                <a className="rounded-xl border border-slate-200 p-4 transition hover:border-blue-300 hover:bg-blue-50" href={`mailto:${developerInfo.email}`}>
                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Email</div>
                  <div className="mt-1 text-slate-900">{developerInfo.email}</div>
                </a>
                <a className="rounded-xl border border-slate-200 p-4 transition hover:border-blue-300 hover:bg-blue-50" href={developerInfo.url} target="_blank" rel="noreferrer">
                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">GitHub</div>
                  <div className="mt-1 text-slate-900">{developerInfo.url}</div>
                </a>
                <a className="rounded-xl border border-slate-200 p-4 transition hover:border-blue-300 hover:bg-blue-50" href={developerInfo.linkedin} target="_blank" rel="noreferrer">
                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">LinkedIn</div>
                  <div className="mt-1 text-slate-900">{developerInfo.linkedin}</div>
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeveloperPage;
