import { useEffect } from 'react';
import { Provider } from 'react-redux';

import Dashboard from 'pages/Dashboard';
import { useAction } from 'redux/hooks';
import { swarmActions } from 'redux/slice/swarm.slice';
import { uiActions } from 'redux/slice/ui.slice';
import { store } from 'redux/store';
import { ITab } from 'types/tab.types';

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
  [key in StatKey | 'name' | 'safeName']: string;
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

export default function LocustUi<TabType extends string = string, StatKey extends string = string>({
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
    <Provider store={store}>
      <Dashboard extendedTabs={extendedTabs} />
    </Provider>
  );
}
