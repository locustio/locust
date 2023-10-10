import { useEffect, useRef, useState } from 'react';

import { SWARM_STATE } from 'constants/swarm';
import useInterval from 'hooks/useInterval';
import { useGetExceptionsQuery, useGetStatsQuery, useGetTasksQuery } from 'redux/api/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { swarmActions } from 'redux/slice/swarm.slice';
import { uiActions } from 'redux/slice/ui.slice';
import { roundToDecimalPlaces } from 'utils/number';

export default function useSwarmUi() {
  const setSwarm = useAction(swarmActions.setSwarm);
  const setUi = useAction(uiActions.setUi);
  const updateCharts = useAction(uiActions.updateCharts);
  const updateChartMarkers = useAction(uiActions.updateChartMarkers);
  const swarm = useSelector(({ swarm }) => swarm);
  const previousSwarmState = useRef(swarm.state);
  const [shouldAddMarker, setShouldAddMarker] = useState(false);

  const { data: statsData, refetch: refetchStats } = useGetStatsQuery();
  const { data: tasksData, refetch: refetchTasks } = useGetTasksQuery();
  const { data: exceptionsData, refetch: refetchExceptions } = useGetExceptionsQuery();

  useEffect(() => {
    if (!statsData) {
      return;
    }

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
    } = statsData;

    if (state === SWARM_STATE.STOPPED || state === SWARM_STATE.SPAWNING) {
      setSwarm({ state });
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
  }, [statsData]);

  useEffect(() => {
    if (tasksData) {
      setUi({ ratios: tasksData });
    }
  }, [tasksData]);

  useEffect(() => {
    if (exceptionsData) {
      setUi({ exceptions: exceptionsData.exceptions });
    }
  }, [exceptionsData]);

  useInterval(refetchStats, 2000, { shouldRunInterval: swarm.state !== SWARM_STATE.STOPPED });
  useInterval(refetchTasks, 5000, { shouldRunInterval: swarm.state !== SWARM_STATE.STOPPED });
  useInterval(refetchExceptions, 5000, { shouldRunInterval: swarm.state !== SWARM_STATE.STOPPED });

  useEffect(() => {
    if (swarm.state === SWARM_STATE.RUNNING && previousSwarmState.current === SWARM_STATE.STOPPED) {
      setShouldAddMarker(true);
    }

    previousSwarmState.current = swarm.state;
  }, [swarm.state, previousSwarmState]);
}
