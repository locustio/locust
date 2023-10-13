import { Link, List, ListItem } from '@mui/material';
import { connect } from 'react-redux';

import { THEME_MODE } from 'constants/theme';
import { ISwarmState } from 'redux/slice/swarm.slice';
import { IRootState } from 'redux/store';
import { objectToQueryString } from 'utils/string';

interface IReports extends Pick<ISwarmState, 'extendedCsvFiles' | 'statsHistoryEnabled'> {
  isDarkMode: boolean;
  groupFailuresBy?: string;
  groupStatsBy?: string;
}

function Reports({
  extendedCsvFiles,
  groupFailuresBy,
  groupStatsBy,
  isDarkMode,
  statsHistoryEnabled,
}: IReports) {
  return (
    <List sx={{ display: 'flex', flexDirection: 'column' }}>
      <ListItem>
        <Link href={`/stats/requests/csv${objectToQueryString({ groupBy: groupStatsBy })}`}>
          Download requests CSV
        </Link>
      </ListItem>
      {statsHistoryEnabled && (
        <ListItem>
          <Link href='/stats/requests_full_history/csv'>
            Download full request statistics history CSV
          </Link>
        </ListItem>
      )}
      <ListItem>
        <Link href={`/stats/failures/csv${objectToQueryString({ groupBy: groupFailuresBy })}`}>
          Download failures CSV
        </Link>
      </ListItem>
      <ListItem>
        <Link href='/exceptions/csv'>Download exceptions CSV</Link>
      </ListItem>
      <ListItem>
        <Link
          href={`/stats/report${objectToQueryString({
            theme: isDarkMode ? THEME_MODE.DARK : THEME_MODE.LIGHT,
            groupStatsBy,
            groupFailuresBy,
          })}`}
          target='_blank'
        >
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

const storeConnector = ({
  theme: { isDarkMode },
  swarm: { extendedCsvFiles, statsHistoryEnabled },
  ui: {
    tables: { stats: statsTableState, failures: failuresTableState },
  },
}: IRootState) => ({
  extendedCsvFiles,
  groupFailuresBy: failuresTableState && failuresTableState.groupBy,
  groupStatsBy: statsTableState && statsTableState.groupBy,
  isDarkMode,
  statsHistoryEnabled,
});

export default connect(storeConnector)(Reports);
