import { Link, List, ListItem } from '@mui/material';
import { connect } from 'react-redux';

import { ISwarmState } from 'redux/slice/swarm.slice';
import { IRootState } from 'redux/store';

function Reports({
  extendedCsvFiles,
  statsHistoryEnabled,
}: Pick<ISwarmState, 'extendedCsvFiles' | 'statsHistoryEnabled'>) {
  return (
    <List sx={{ display: 'flex', flexDirection: 'column' }}>
      <ListItem>
        <Link href='/stats/requests/csv'>Download requests CSV</Link>
      </ListItem>
      {statsHistoryEnabled && (
        <ListItem>
          <Link href='/stats/requests_full_history/csv'>
            Download full request statistics history CSV
          </Link>
        </ListItem>
      )}
      <ListItem>
        <Link href='/stats/failures/csv'>Download failures CSV</Link>
      </ListItem>
      <ListItem>
        <Link href='/exceptions/csv'>Download exceptions CSV</Link>
      </ListItem>
      <ListItem>
        <Link href='/stats/report' target='_blank'>
          Download Report
        </Link>
      </ListItem>
      {extendedCsvFiles &&
        extendedCsvFiles.map(({ href, title }) => (
          <ListItem>
            <Link href={href}>{title}</Link>
          </ListItem>
        ))}
    </List>
  );
}

const storeConnector = ({ swarm: { extendedCsvFiles, statsHistoryEnabled } }: IRootState) => ({
  extendedCsvFiles,
  statsHistoryEnabled,
});

export default connect(storeConnector)(Reports);
