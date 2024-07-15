import { ReactNode, useEffect } from 'react';
import { Provider as ReactReduxProvider } from 'react-redux';
import { TypedUseSelectorHook, useSelector as useReduxSelector } from 'react-redux';

import Dashboard from 'pages/Dashboard';
import { useAction } from 'redux/hooks';
import { swarmActions } from 'redux/slice/swarm.slice';
import { uiActions } from 'redux/slice/ui.slice';
import { IRootState, store } from 'redux/store';
import { ITab } from 'types/tab.types';
export type { IRootState } from 'redux/store';

export const useSelector: TypedUseSelectorHook<IRootState> = useReduxSelector;

export const locustStore = store;

export type { ITab } from 'types/tab.types';

export interface IExtendedTableStructure<StatKey> {
  key: StatKey | 'name' | 'method';
  title: string;
}

export interface IExtendedTable<TabType, StatKey> {
  key: TabType;
  structure: IExtendedTableStructure<StatKey>[];
}

export interface IExtendedReport {
  href: string;
  title: string;
}

export type IStatData<StatKey extends string> = {
  [key in StatKey]: string;
} & {
  name: string;
  safeName: string;
};

export interface IExtendedStat<TabType, StatKey extends string> {
  key: TabType;
  data: IStatData<StatKey>[];
}

export interface ILocustUi<TabType, StatKeys extends string> {
  extendedTabs: ITab<TabType>[];
  extendedTables: IExtendedTable<TabType, StatKeys>[];
  extendedReports: IExtendedReport[];
  extendedStats: IExtendedStat<TabType, StatKeys>[];
}

export function LocustProvider({ children }: { children: ReactNode }) {
  return <ReactReduxProvider store={store}>{children}</ReactReduxProvider>;
}

export default function LocustUi<TabType extends string, StatKey extends string>({
  extendedTabs,
  extendedTables,
  extendedReports,
  extendedStats,
}: ILocustUi<TabType, StatKey>) {
  const setSwarm = useAction(swarmActions.setSwarm, store.dispatch);
  const setUi = useAction(uiActions.setUi, store.dispatch);

  useEffect(() => {
    setSwarm({ extendedTables, extendedCsvFiles: extendedReports });
  }, [extendedTables, extendedReports]);

  useEffect(() => {
    setUi({ extendedStats });
  }, [extendedStats]);

  return (
    <LocustProvider>
      <Dashboard extendedTabs={extendedTabs} />
    </LocustProvider>
  );
}
