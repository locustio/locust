import { useEffect } from 'react';
import { Provider } from 'react-redux';

import Dashboard from 'pages/Dashboard';
import { useAction } from 'redux/hooks';
import { swarmActions } from 'redux/slice/swarm.slice';
import { uiActions } from 'redux/slice/ui.slice';
import { store } from 'redux/store';
import { ITab } from 'types/tab.types';
export { default as Table } from 'components/Table/Table';
export { default as LineChart } from 'components/LineChart/LineChart';
export { baseTabs } from 'components/Tabs/Tabs.constants';
export { default as useInterval } from 'hooks/useInterval';
export { roundToDecimalPlaces } from 'utils/number';
export { SWARM_STATE } from 'constants/swarm';
export type { IRootState } from 'redux/store';

export type { ITab } from 'types/tab.types';

export interface IExtendedTableStructure<StatKey> {
  key: StatKey | 'name' | 'method';
  title: string;
}

export interface IExtendedTable<ExtendedTabKey, StatKey> {
  key: ExtendedTabKey;
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

export interface IExtendedStat<ExtendedTabKey, StatKey extends string> {
  key: ExtendedTabKey;
  data: IStatData<StatKey>[];
}

export interface ILocustUi<ExtendedTabKey, StatKeys extends string> {
  extendedTabs?: ITab<ExtendedTabKey>[];
  extendedTables?: IExtendedTable<ExtendedTabKey, StatKeys>[];
  extendedReports?: IExtendedReport[];
  extendedStats?: IExtendedStat<ExtendedTabKey, StatKeys>[];
  tabs?: ITab[];
}

export default function LocustUi<
  ExtendedTabKey extends string = string,
  StatKey extends string = string,
>({
  extendedTabs,
  extendedTables,
  extendedReports,
  extendedStats,
  tabs,
}: ILocustUi<ExtendedTabKey, StatKey>) {
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
      <Dashboard extendedTabs={extendedTabs} tabs={tabs} />
    </Provider>
  );
}
