import { useEffect, useRef, useState } from 'react';

import { SWARM_STATE } from 'constants/swarm';
import useInterval from 'hooks/useInterval';
import { useGetStatsQuery } from 'redux/api/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { swarmActions } from 'redux/slice/swarm.slice';
import { uiActions } from 'redux/slice/ui.slice';
import { roundToDecimalPlaces } from 'utils/number';

const STATS_REFETCH_INTERVAL = 2000;

export default function useFetchStats() {
  const setSwarm = useAction(swarmActions.setSwarm);
  const setUi = useAction(uiActions.setUi);
  const updateCharts = useAction(uiActions.updateCharts);
  const updateChartMarkers = useAction(uiActions.updateChartMarkers);
  const swarm = useSelector(({ swarm }) => swarm);
  const previousSwarmState = useRef(swarm.state);
  const [shouldAddMarker, setShouldAddMarker] = useState(false);

  const { data: statsData, refetch: refetchStats } = useGetStatsQuery();

  const shouldRunRefetchInterval =
    swarm.state === SWARM_STATE.SPAWNING || swarm.state == SWARM_STATE.RUNNING;

  useEffect(() => {
    if (!statsData) {
      return;
    }

    const {
      state,
      currentResponseTimePercentiles,
      extendedStats,
      stats,
      errors,
      totalRps,
      totalFailPerSec,
      failRatio,
      workers,
      userCount,
      totalAvgResponseTime,
    } = statsData;

    const time = new Date().toISOString();

    if (shouldAddMarker) {
      setShouldAddMarker(false);
      updateChartMarkers(time);
    }

    const totalRpsRounded = roundToDecimalPlaces(totalRps, 2);
    const totalFailPerSecRounded = roundToDecimalPlaces(totalFailPerSec, 2);
    const totalFailureRatioRounded = roundToDecimalPlaces(failRatio * 100);

    const percentilesWithTime = Object.entries(currentResponseTimePercentiles).reduce(
      (percentiles, [key, value]) => ({
        ...percentiles,
        [key]: [time, value || 0],
      }),
      {},
    );

    const newChartEntry = {
      ...percentilesWithTime,
      currentRps: [time, totalRpsRounded],
      currentFailPerSec: [time, totalFailPerSecRounded],
      totalAvgResponseTime: [time, roundToDecimalPlaces(totalAvgResponseTime, 2)],
      userCount: [time, userCount],
      time,
    };

    setUi({
      extendedStats,
      stats,
      errors,
      totalRps: totalRpsRounded,
      failRatio: totalFailureRatioRounded,
      workers,
      userCount,
    });
    updateCharts(newChartEntry);

    setSwarm({ state });
  }, [statsData]);

  useInterval(refetchStats, STATS_REFETCH_INTERVAL, {
    shouldRunInterval: shouldRunRefetchInterval,
  });

  useEffect(() => {
    if (swarm.state === SWARM_STATE.RUNNING && previousSwarmState.current === SWARM_STATE.STOPPED) {
      setShouldAddMarker(true);
    }

    previousSwarmState.current = swarm.state;
  }, [swarm.state, previousSwarmState]);
}
