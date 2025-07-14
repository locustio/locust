import { connect } from 'react-redux';

import FailuresTable from 'components/FailuresTable/FailuresTable';
import { IRootState } from 'redux/store';

const storeConnector = ({ ui: { errors } }: IRootState) => ({ errors });

export default connect(storeConnector)(FailuresTable);
