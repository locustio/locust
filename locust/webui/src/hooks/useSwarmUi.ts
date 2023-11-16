import { useEffect, useRef, useState } from 'react';

import { SWARM_STATE } from 'constants/swarm';
import useInterval from 'hooks/useInterval';
import { useGetExceptionsQuery, useGetStatsQuery, useGetTasksQuery } from 'redux/api/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { swarmActions } from 'redux/slice/swarm.slice';
import { uiActions } from 'redux/slice/ui.slice';
import { roundToDecimalPlaces } from 'utils/number';

const STATS_REFETCH_INTERVAL = 2000;

export default function useSwarmUi() {
  const setSwarm = useAction(swarmActions.setSwarm);
  const setUi = useAction(uiActions.setUi);
  const updateCharts = useAction(uiActions.updateCharts);
  const updateChartMarkers = useAction(uiActions.updateChartMarkers);
  const swarm = useSelector(({ swarm }) => swarm);
  const previousSwarmState = useRef(swarm.state);
  const hasSetInitStats = useRef(false);
  const [shouldAddMarker, setShouldAddMarker] = useState(false);

  const { data: statsData, refetch: refetchStats } = useGetStatsQuery();
  const { data: tasksData, refetch: refetchTasks } = useGetTasksQuery();
  const { data: exceptionsData, refetch: refetchExceptions } = useGetExceptionsQuery();

  const shouldRunRefetchInterval =
    swarm.state === SWARM_STATE.SPAWNING || swarm.state == SWARM_STATE.RUNNING;

  const updateStatsUi = () => {
    if (!statsData) {
      return;
    }

    const {
      extendedStats,
      stats,
      errors,
      totalRps,
      failRatio,
      workers,
      currentResponseTimePercentile1,
      currentResponseTimePercentile2,
      userCount,
    } = statsData;

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
  };

  useEffect(() => {
    if (
      statsData &&
      (statsData.state === SWARM_STATE.STOPPED || statsData.state === SWARM_STATE.SPAWNING)
    ) {
      setSwarm({ state: statsData.state });
    }
  }, [statsData && statsData.state]);

  useEffect(() => {
    if (statsData) {
      if (!hasSetInitStats.current) {
        // handle setting stats on first load
        updateStatsUi();
      }

      hasSetInitStats.current = true;
    }
  }, [statsData]);

  useInterval(updateStatsUi, STATS_REFETCH_INTERVAL, {
    shouldRunInterval: !!statsData && shouldRunRefetchInterval,
  });

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

  useInterval(refetchStats, STATS_REFETCH_INTERVAL, {
    shouldRunInterval: shouldRunRefetchInterval,
  });
  useInterval(refetchTasks, 5000, {
    shouldRunInterval: shouldRunRefetchInterval,
  });
  useInterval(refetchExceptions, 5000, {
    shouldRunInterval: shouldRunRefetchInterval,
  });

  useEffect(() => {
    if (swarm.state === SWARM_STATE.RUNNING && previousSwarmState.current === SWARM_STATE.STOPPED) {
      setShouldAddMarker(true);
    }

    previousSwarmState.current = swarm.state;
  }, [swarm.state, previousSwarmState]);
}
