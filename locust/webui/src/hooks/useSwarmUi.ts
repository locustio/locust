import { useEffect, useRef, useState } from 'react';

import { asyncRequest } from 'api/asyncRequest';
import { SWARM_STATE } from 'constants/swarm';
import useAsync from 'hooks/useAsync';
import useInterval from 'hooks/useInterval';
import { useAction, useSelector } from 'redux/hooks';
import { swarmActions } from 'redux/slice/swarm.slice';
import { uiActions } from 'redux/slice/ui.slice';
import { IStatsResponse, ISwarmException, ISwarmRatios } from 'types/ui.types';
import { roundToDecimalPlaces } from 'utils/number';

export default function useSwarmUi() {
  const setSwarm = useAction(swarmActions.setSwarm);
  const setUi = useAction(uiActions.setUi);
  const updateCharts = useAction(uiActions.updateCharts);
  const updateChartMarkers = useAction(uiActions.updateChartMarkers);
  const swarm = useSelector(({ swarm }) => swarm);
  const previousSwarmState = useRef(swarm.state);
  const [shouldAddMarker, setShouldAddMarker] = useState(false);

  const { execute: updateStats } = useAsync(async () => {
    const {
      extendedStats,
      state,
      stats,
      errors,
      totalRps,
      failRatio,
      workers,
      currentResponseTimePercentile1,
      currentResponseTimePercentile2,
      userCount,
    } = (await asyncRequest('stats/requests')) as IStatsResponse;

    if (state === SWARM_STATE.STOPPED) {
      setSwarm({ state: SWARM_STATE.STOPPED });
    }

    const time = new Date().toLocaleTimeString();

    if (shouldAddMarker) {
      setShouldAddMarker(false);
      updateChartMarkers(time);
    }

    const totalRpsRounded = roundToDecimalPlaces(totalRps, 2);
    const toalFailureRounded = roundToDecimalPlaces(failRatio * 100);

    const newChartEntry = {
      currentRps: totalRpsRounded,
      currentFailPerSec: failRatio,
      responseTimePercentile1: currentResponseTimePercentile1,
      responseTimePercentile2: currentResponseTimePercentile2,
      userCount: userCount,
      time,
    };

    setUi({
      extendedStats,
      stats,
      errors,
      totalRps: totalRpsRounded,
      failRatio: toalFailureRounded,
      workers,
      userCount,
    });
    updateCharts(newChartEntry);
  });

  const { execute: getTasks } = useAsync(async () => {
    const ratios = (await asyncRequest('tasks')) as ISwarmRatios;

    setUi({ ratios });
  });

  const { execute: getExceptions } = useAsync(async () => {
    const { exceptions } = (await asyncRequest('exceptions')) as { exceptions: ISwarmException[] };

    setUi({ exceptions });
  });

  useInterval(updateStats, 2000, { shouldRunInterval: swarm.state === SWARM_STATE.RUNNING });
  useInterval(getTasks, 5000, { shouldRunInterval: swarm.state === SWARM_STATE.RUNNING });
  useInterval(getExceptions, 5000, { shouldRunInterval: swarm.state === SWARM_STATE.RUNNING });

  useEffect(() => {
    if (swarm.state === SWARM_STATE.RUNNING && previousSwarmState.current === SWARM_STATE.STOPPED) {
      setShouldAddMarker(true);
    }

    previousSwarmState.current = swarm.state;
  }, [swarm.state, previousSwarmState]);

  useEffect(() => {
    // Handle showing test history on first load
    updateStats();
    getTasks();
  }, []);
}
