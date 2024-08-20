import { ComponentType } from 'react';

import { IRootState } from 'redux/store';

export interface ITab<TabType = string> {
  component?: ComponentType;
  key: TabType;
  title: string;
  shouldDisplayTab?: (state: IRootState) => boolean;
}
