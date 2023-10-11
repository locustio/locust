import { connect } from 'react-redux';

import { IUiState } from 'redux/slice/ui.slice';
import { IRootState } from 'redux/store';
import { IClassRatio } from 'types/ui.types';

function getRatioPercent(ratio: number) {
  return (ratio * 100).toFixed(1) + '%';
}

function NestedRatioList({ classRatio }: { classRatio: IClassRatio }) {
  return (
    <ul>
      {Object.entries(classRatio).map(([key, { ratio, tasks }]) => (
        <li key={`nested-ratio-${key}`}>
          {`${getRatioPercent(ratio)} ${key}`}
          {tasks && <NestedRatioList classRatio={tasks} />}
        </li>
      ))}
    </ul>
  );
}

export function SwarmRatios({ ratios: { perClass, total } }: { ratios: IUiState['ratios'] }) {
  if (!perClass && !total) {
    return null;
  }

  return (
    <div>
      {perClass && (
        <>
          <h3>Ratio Per Class</h3>
          <NestedRatioList classRatio={perClass} />
        </>
      )}

      {total && (
        <>
          <h3>Total Ratio</h3>
          <NestedRatioList classRatio={total} />
        </>
      )}
    </div>
  );
}

const storeConnector = ({ ui: { ratios } }: IRootState) => ({
  ratios,
});

export default connect(storeConnector)(SwarmRatios);
