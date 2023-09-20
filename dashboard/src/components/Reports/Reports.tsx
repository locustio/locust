import { Link, List, ListItem } from '@mui/material';

import { useSelector } from 'redux/hooks';

export default function Reports() {
  const statsHistoryEnabled = useSelector(({ swarm }) => swarm.statsHistoryEnabled);

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
        <Link href='./stats/failures/csv'>Download failures CSV</Link>
      </ListItem>
      <ListItem>
        <Link href='/exceptions/csv'>Download exceptions CSV</Link>
      </ListItem>
      <ListItem>
        <Link href='/stats/report' target='_blank'>
          Download Report
        </Link>
      </ListItem>
    </List>
  );
}
