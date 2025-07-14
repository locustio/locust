import { connect } from 'react-redux';

import SwarmRatios from 'components/SwarmRatios/SwarmRatios';
import { IRootState } from 'redux/store';

const storeConnector = ({ ui: { ratios } }: IRootState) => ({
  ratios,
});

export default connect(storeConnector)(SwarmRatios);
