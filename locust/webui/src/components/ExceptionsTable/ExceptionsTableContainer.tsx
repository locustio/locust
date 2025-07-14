import { connect } from 'react-redux';

import ExceptionsTable from 'components/ExceptionsTable/ExceptionsTable';
import { IRootState } from 'redux/store';

const storeConnector = ({ ui: { exceptions } }: IRootState) => ({ exceptions });

export default connect(storeConnector)(ExceptionsTable);
