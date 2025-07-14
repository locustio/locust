import { connect } from 'react-redux';

import StatsTable from 'components/StatsTable/StatsTable';
import { IRootState } from 'redux/store';

const storeConnector = ({ ui: { stats } }: IRootState) => ({ stats });

export default connect(storeConnector)(StatsTable);
