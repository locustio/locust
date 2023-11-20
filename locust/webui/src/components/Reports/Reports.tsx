import { Link, List, ListItem } from '@mui/material';
import { connect } from 'react-redux';

import { THEME_MODE } from 'constants/theme';
import { useSelector } from 'redux/hooks';
import { ISwarmState } from 'redux/slice/swarm.slice';
import { IRootState } from 'redux/store';

function Reports({
  extendedCsvFiles,
  statsHistoryEnabled,
}: Pick<ISwarmState, 'extendedCsvFiles' | 'statsHistoryEnabled'>) {
  const isDarkMode = useSelector(({ theme: { isDarkMode } }) => isDarkMode);

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
        <Link
          href={`/stats/report?theme=${isDarkMode ? THEME_MODE.DARK : THEME_MODE.LIGHT}`}
          target='_blank'
        >
          Download Report
        </Link>
      </ListItem>
      {extendedCsvFiles &&
        extendedCsvFiles.map(({ href, title }, index) => (
          <ListItem key={`extended-csv-${index}`}>
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
