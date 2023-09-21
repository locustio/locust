import { IRootState } from 'redux/store';

export interface ITab {
  component: React.ComponentType;
  key: string;
  title: string;
  shouldDisplayTab?: (state: IRootState) => boolean;
}
