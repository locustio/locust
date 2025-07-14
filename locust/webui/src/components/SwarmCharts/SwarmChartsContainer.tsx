import { connect } from 'react-redux';

import SwarmCharts from 'components/SwarmCharts/SwarmCharts';
import { IRootState } from 'redux/store';

const storeConnector = ({ theme: { isDarkMode }, ui: { charts } }: IRootState) => ({
  charts,
  isDarkMode,
});

export default connect(storeConnector)(SwarmCharts);
