import RefreshIcon from '@mui/icons-material/Refresh';
import {
    Alert,
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Box,
    Button,
    CircularProgress,
    Divider,
    IconButton,
    Paper,
    TextField,
    Tooltip,
    Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { SWARM_STATE } from 'constants/swarm';
import { useAction, useSelector } from 'redux/hooks';
import { uiActions } from 'redux/slice/ui.slice';
import { swarmActions } from 'redux/slice/swarm.slice';

const API_URL = 'http://34.71.3.151/start-test';
const STATUS_API_URL = 'http://34.71.3.151/test-status';
const QUALITY_METRICS_HTML_BASE = 'http://34.71.3.151/quality-metrics-html';
const TEST_RESULTS_BASE = 'http://34.71.3.151/test-results';

const TEST_RESULTS_POLL_MS = 5_000;

const DEFAULT_DATASET_JSON = JSON.stringify(
    {
        id: '1',
        event: false,
        inputs: [
            {
                pred_colname: 'TEXT',
                datatype: 'BYTES',
                shape: [1, 1],
                data: [
                    '{"window_title": "Google search", "org_type": "Primary", "capture": "Where can I buy ice cream?", "capture_id": "123"}',
                ],
            },
        ],
    },
    null,
    2,
);

function parseDatasetJson(text: string): { ok: true; dataset: unknown[] } | { ok: false; message: string } {
    const trimmed = text.trim();
    if (!trimmed) {
        return { ok: false, message: 'Dataset JSON is required' };
    }
    try {
        const parsed = JSON.parse(trimmed) as unknown;
        if (Array.isArray(parsed)) {
            return { ok: true, dataset: parsed };
        }
        if (parsed && typeof parsed === 'object') {
            return { ok: true, dataset: [parsed] };
        }
        return { ok: false, message: 'Dataset JSON must be an object or array' };
    } catch {
        return { ok: false, message: 'Invalid dataset JSON' };
    }
}

type TestResultsResponse = {
    test_id?: string;
    status?: string;
    message?: string;
    progress?: number;
    summary?: unknown[];
    locust_stats?: Record<string, unknown>;
    telemetry_data?: unknown[];
    duration_seconds?: number;
    reports?: { csv?: string };
    config?: Record<string, unknown>;
};

type StartTestResponse = {
    success: boolean;
    test_id: string;
    status?: string;
    message?: string;
    config?: {
        users?: number;
        spawn_rate?: number;
        target?: string;
        dataset_size?: number;
    };
    endpoints?: {
        status: string;
        results: string;
        download_html: string;
        download_csv: string;
    };
};

export default function TestTab() {
    const [testId, setTestId] = useState('test_1');
    const [host, setHost] = useState('https://us-central1-aiplatform.googleapis.com');
    const [path, setPath] = useState(
        '/v1/projects/fzo-edu-ds/locations/us-central1/endpoints/8045470177820672000:rawPredict',
    );
    const [users, setUsers] = useState<number>(200);
    const [spawnRate, setSpawnRate] = useState<number>(5);
    const [randomize, setRandomize] = useState<boolean>(true);
    const [runTime, setRunTime] = useState<number>(90);
    const [batchSize, setBatchSize] = useState<number>(1);
    const [authorization, setAuthorization] = useState<string>('Bearer {Paste the Token}');
    const [authorizationError, setAuthorizationError] = useState(false);

    // Keep these as separate fields so you can see/edit each payload property directly.
    const [truthCol, setTruthCol] = useState('event');
    const [predCol, setPredCol] = useState('predicted_label');
    const [severityCol, setSeverityCol] = useState('');
    const [nonEventValue, setNonEventValue] = useState('');
    const [nonAlertValue, setNonAlertValue] = useState('');
    const [alertValue, setAlertValue] = useState('');
    const [criticalLevel, setCriticalLevel] = useState('');

    const [qualityTestsJson, setQualityTestsJson] = useState('["accuracy"]');

    const [datasetJson, setDatasetJson] = useState(DEFAULT_DATASET_JSON);

    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isPollingStarted, setIsPollingStarted] = useState(false);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [response, setResponse] = useState<StartTestResponse | null>(null);
    const setSwarm = useAction(swarmActions.setSwarm);
    const setUi = useAction(uiActions.setUi);

    type TestStatusResponse = {
        status?: string;
        created_at?: string;
        config?: Record<string, unknown>;
        start_time?: string;
        progress?: number;
        total_users?: number;
        mode?: string;
        data_points?: number;
        swarm_started?: boolean;
        completed_requests?: number;
        elapsed_seconds?: number;
        current_users?: number;
        rps?: number;
        error_rate?: number;
        state?: string;
        quality_metrics?: { info?: string };
        reports?: { csv?: string };
        end_time?: string;
        final_stats?: Record<string, unknown>;
        total_requests?: number;
    };

    const [isFetchingStatus, setIsFetchingStatus] = useState(false);
    const [statusErrorMessage, setStatusErrorMessage] = useState<string | null>(null);
    const [statusResponse, setStatusResponse] = useState<TestStatusResponse | null>(null);

    const swarmState = useSelector(({ swarm }) => swarm.state);
    const [testResults, setTestResults] = useState<TestResultsResponse | null>(null);
    const [testResultsLoading, setTestResultsLoading] = useState(false);
    const [testResultsError, setTestResultsError] = useState<string | null>(null);
    const [testResultsPolling, setTestResultsPolling] = useState(false);

    const [qualityMetricsHtml, setQualityMetricsHtml] = useState<string | null>(null);
    const [qualityMetricsLoading, setQualityMetricsLoading] = useState(false);
    const [qualityMetricsError, setQualityMetricsError] = useState<string | null>(null);

    const fetchTestResultsJson = async (): Promise<TestResultsResponse> => {
        const res = await fetch(`${TEST_RESULTS_BASE}/${encodeURIComponent(testId)}`, {
            method: 'GET',
            headers: { accept: 'application/json' },
        });
        if (!res.ok) {
            throw new Error(`Test results failed (${res.status})`);
        }
        return (await res.json()) as TestResultsResponse;
    };

    const fetchQualityMetricsHtml = async () => {
        setQualityMetricsLoading(true);
        setQualityMetricsError(null);
        try {
            const res = await fetch(`${QUALITY_METRICS_HTML_BASE}/${encodeURIComponent(testId)}`, {
                method: 'GET',
                headers: { accept: 'text/html' },
            });
            if (!res.ok) {
                throw new Error(`Request failed (${res.status})`);
            }
            const html = await res.text();
            setQualityMetricsHtml(html);
        } catch (err) {
            setQualityMetricsError(err instanceof Error ? err.message : 'Failed to load HTML');
        } finally {
            setQualityMetricsLoading(false);
        }
    };

    const onGetTestResult = async () => {
        if (!testId) return;
        setTestResultsError(null);
        setTestResultsLoading(true);
        try {
            const data = await fetchTestResultsJson();
            setTestResults(data);
        } catch (err) {
            setTestResultsError(err instanceof Error ? err.message : 'Request failed');
        } finally {
            setTestResultsLoading(false);
        }
    };

    const onGetQualityMetricsHtml = async () => {
        if (!testId) return;
        await fetchQualityMetricsHtml();
    };

    useEffect(() => {
        if (swarmState !== SWARM_STATE.STOPPED) {
            setTestResultsPolling(false);
            setTestResultsLoading(false);
            return;
        }

        if (!testId) return;

        let cancelled = false;
        let intervalId: ReturnType<typeof setInterval> | null = null;

        const pollOnce = async (): Promise<boolean> => {
            const res = await fetch(`${TEST_RESULTS_BASE}/${encodeURIComponent(testId)}`, {
                method: 'GET',
                headers: { accept: 'application/json' },
            });
            if (!res.ok) {
                throw new Error(`Test results failed (${res.status})`);
            }
            const data = (await res.json()) as TestResultsResponse;
            if (!cancelled) {
                setTestResults(data);
            }
            return data.status === 'running';
        };

        const runQualityAfterResults = async () => {
            if (cancelled) return;
            setQualityMetricsLoading(true);
            setQualityMetricsError(null);
            try {
                const res = await fetch(`${QUALITY_METRICS_HTML_BASE}/${encodeURIComponent(testId)}`, {
                    method: 'GET',
                    headers: { accept: 'text/html' },
                });
                if (!res.ok) {
                    throw new Error(`Request failed (${res.status})`);
                }
                const html = await res.text();
                if (!cancelled) {
                    setQualityMetricsHtml(html);
                }
            } catch (err) {
                if (!cancelled) {
                    setQualityMetricsError(err instanceof Error ? err.message : 'Failed to load HTML');
                }
            } finally {
                if (!cancelled) {
                    setQualityMetricsLoading(false);
                }
            }
        };

        void (async () => {
            setTestResultsError(null);
            setTestResultsLoading(true);
            setTestResultsPolling(false);
            try {
                const stillRunning = await pollOnce();
                if (cancelled) return;
                setTestResultsLoading(false);

                if (!stillRunning) {
                    await runQualityAfterResults();
                    return;
                }

                setTestResultsPolling(true);
                intervalId = setInterval(() => {
                    void (async () => {
                        try {
                            const running = await pollOnce();
                            if (cancelled) return;
                            if (!running) {
                                if (intervalId !== null) {
                                    clearInterval(intervalId);
                                    intervalId = null;
                                }
                                setTestResultsPolling(false);
                                await runQualityAfterResults();
                            }
                        } catch (err) {
                            if (!cancelled) {
                                setTestResultsError(err instanceof Error ? err.message : 'Poll failed');
                            }
                            if (intervalId !== null) {
                                clearInterval(intervalId);
                                intervalId = null;
                            }
                            setTestResultsPolling(false);
                        }
                    })();
                }, TEST_RESULTS_POLL_MS);
            } catch (err) {
                if (!cancelled) {
                    setTestResultsError(err instanceof Error ? err.message : 'Failed to load test results');
                }
                setTestResultsLoading(false);
            }
        })();

        return () => {
            cancelled = true;
            if (intervalId !== null) {
                clearInterval(intervalId);
            }
        };
    }, [swarmState, testId]);

    const apiOrigin = useMemo(() => {
        try {
            return new URL(API_URL).origin;
        } catch {
            return '';
        }
    }, []);

    const submitDisabled = isSubmitting || isPollingStarted || !testId || !host || !path;

    const buildPayload = (dataset: unknown[]) => {
        let qualityTests: unknown[] = [];
        try {
            qualityTests = JSON.parse(qualityTestsJson) as unknown[];
        } catch {
            qualityTests = [];
        }

        return {
            test_id: testId,
            host,
            path,
            users,
            spawn_rate: spawnRate,
            randomize,
            run_time: runTime,
            batch_size: batchSize,
            headers: {
                Authorization: authorization,
                'Content-Type': 'application/json',
            },
            quality_tests: qualityTests,
            config: {
                truth_col: truthCol,
                pred_col: predCol,
                severity_col: severityCol,
                non_event_value: nonEventValue,
                non_alert_value: nonAlertValue,
                alert_value: alertValue,
                critical_level: criticalLevel,
            },
            dataset,
        };
    };

    const onSubmit = async () => {
        const isAuthorizationEmpty = authorization.trim().length === 0;
        if (isAuthorizationEmpty) {
            setAuthorizationError(true);
            return;
        }

        setAuthorizationError(false);
        setErrorMessage(null);
        setResponse(null);

        const datasetParsed = parseDatasetJson(datasetJson);
        if (!datasetParsed.ok) {
            setErrorMessage(datasetParsed.message);
            return;
        }

        setIsSubmitting(true);
        try {
            const payload = buildPayload(datasetParsed.dataset);
            const res = await fetch(API_URL, {
                method: 'POST',
                headers: { 'content-type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = (await res.json()) as StartTestResponse;
            setResponse(data);

            if (!data?.success) {
                setErrorMessage(data?.message || 'Request failed');
                return;
            }

            // Poll until backend reports `swarm_started: true`, then flip redux state.
            setIsPollingStarted(true);
            const startedAt = Date.now();
            const maxWaitMs = 60_000;
            const pollEveryMs = 5_000;

            const pollOnce = async () => {
                const statusRes = await fetch(
                    `${STATUS_API_URL}/${encodeURIComponent(testId)}`,
                    {
                        method: 'GET',
                        headers: { accept: 'application/json' },
                    },
                );
                return (await statusRes.json()) as TestStatusResponse;
            };

            while (Date.now() - startedAt < maxWaitMs) {
                const statusData = await pollOnce();
                // Show live status in UI while we wait.
                setStatusResponse(statusData);

                if (statusData?.swarm_started) {
                    // `swarm.state` drives the top navigation (RUNNING/STOPPED) and which
                    // action buttons are visible.
                    setSwarm({
                        state: SWARM_STATE.SPAWNING,
                        host: host,
                        spawnRate: spawnRate,
                        runTime: runTime,
                        userCount: data?.config?.users ?? users,
                    });
                    setUi({
                        // The header "Users" field is based on `ui.userCount`.
                        userCount: data?.config?.users ?? users,
                    });
                    return;
                }

                // Wait before the next poll.
                await new Promise(resolve => setTimeout(resolve, pollEveryMs));
            }

            setErrorMessage('Timed out waiting for swarm to start');
        } catch (err) {
            setErrorMessage(err instanceof Error ? err.message : 'Request failed');
        } finally {
            setIsSubmitting(false);
            setIsPollingStarted(false);
        }
    };

    const onGetStatus = async () => {
        if (!testId) return;

        setStatusErrorMessage(null);
        setIsFetchingStatus(true);

        try {
            const res = await fetch(`${STATUS_API_URL}/${encodeURIComponent(testId)}`, {
                method: 'GET',
                headers: { accept: 'application/json' },
            });

            const data = (await res.json()) as TestStatusResponse;
            setStatusResponse(data);

            if (!data?.status) {
                setStatusErrorMessage('No status returned');
            }
        } catch (err) {
            setStatusErrorMessage(err instanceof Error ? err.message : 'Request failed');
        } finally {
            setIsFetchingStatus(false);
        }
    };

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', rowGap: 2, p: 2 }}>
            <Typography variant='h6' sx={{ fontWeight: 600 }}>
                Run Test
            </Typography>

            <Paper variant='outlined' sx={{ p: 2 }}>
                <Typography variant='subtitle1' sx={{ fontWeight: 700, mb: 1 }}>
                    Start Test Request
                </Typography>

                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
                    <TextField
                        label='test_id'
                        value={testId}
                        onChange={e => setTestId(e.target.value)}
                        fullWidth
                    />
                    <TextField label='host' value={host} onChange={e => setHost(e.target.value)} fullWidth />

                    <TextField
                        label='path'
                        value={path}
                        onChange={e => setPath(e.target.value)}
                        fullWidth
                        sx={{ gridColumn: { xs: '1 / -1', md: 'span 2' } }}
                    />

                    <TextField
                        label='users'
                        type='number'
                        value={users}
                        onChange={e => setUsers(Number(e.target.value))}
                    />
                    <TextField
                        label='spawn_rate'
                        type='number'
                        value={spawnRate}
                        onChange={e => setSpawnRate(Number(e.target.value))}
                    />

                    <TextField
                        label='randomize'
                        value={randomize ? 'true' : 'false'}
                        onChange={e => setRandomize(e.target.value === 'true')}
                        helperText="Use 'true' or 'false'"
                    />
                    <TextField
                        label='run_time'
                        type='number'
                        value={runTime}
                        onChange={e => setRunTime(Number(e.target.value))}
                    />
                    <TextField
                        label='batch_size'
                        type='number'
                        value={batchSize}
                        onChange={e => setBatchSize(Number(e.target.value))}
                        fullWidth
                        sx={{ gridColumn: { xs: '1 / -1', md: 'span 2' } }}
                    />

                    <TextField
                        label='headers.Authorization'
                        value={authorization}
                        onChange={e => {
                            setAuthorization(e.target.value);
                            if (authorizationError && e.target.value.trim().length > 0) {
                                setAuthorizationError(false);
                            }
                        }}
                        error={authorizationError}
                        helperText={authorizationError ? 'Authorization is required' : ''}
                        fullWidth
                        sx={{ gridColumn: { xs: '1 / -1', md: 'span 2' } }}
                        required
                    />

                    <TextField
                        label='quality_tests (JSON array)'
                        value={qualityTestsJson}
                        onChange={e => setQualityTestsJson(e.target.value)}
                        multiline
                        minRows={2}
                        fullWidth
                        sx={{ gridColumn: { xs: '1 / -1', md: 'span 2' } }}
                    />
                </Box>

                <Box sx={{ height: 16 }} />

                <Typography variant='subtitle1' sx={{ fontWeight: 700, mb: 1 }}>
                    Config
                </Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
                    <TextField label='truth_col' value={truthCol} onChange={e => setTruthCol(e.target.value)} />
                    <TextField label='pred_col' value={predCol} onChange={e => setPredCol(e.target.value)} />
                    <TextField
                        label='severity_col'
                        value={severityCol}
                        onChange={e => setSeverityCol(e.target.value)}
                    />
                    <TextField
                        label='non_event_value'
                        value={nonEventValue}
                        onChange={e => setNonEventValue(e.target.value)}
                    />
                    <TextField
                        label='non_alert_value'
                        value={nonAlertValue}
                        onChange={e => setNonAlertValue(e.target.value)}
                    />
                    <TextField label='alert_value' value={alertValue} onChange={e => setAlertValue(e.target.value)} />
                    <TextField
                        label='critical_level'
                        value={criticalLevel}
                        onChange={e => setCriticalLevel(e.target.value)}
                        sx={{ gridColumn: { xs: '1 / -1', md: 'span 2' } }}
                    />
                </Box>

                <Box sx={{ height: 16 }} />

                <Typography variant='subtitle1' sx={{ fontWeight: 700, mb: 1 }}>
                    Dataset
                </Typography>
                <TextField
                    label='dataset (JSON)'
                    value={datasetJson}
                    onChange={e => setDatasetJson(e.target.value)}
                    multiline
                    minRows={14}
                    fullWidth
                    helperText='Sent as the request payload dataset property. Use one JSON object or an array of objects.'
                    inputProps={{ spellCheck: false, style: { fontFamily: 'monospace', fontSize: 13 } }}
                />

                <Box sx={{ display: 'flex', gap: 2, mt: 2, alignItems: 'center' }}>
                    <Button variant='contained' color='primary' onClick={onSubmit} disabled={submitDisabled}>
                        {isSubmitting ? 'Submitting...' : 'Submit'}
                    </Button>
                    {isSubmitting && <CircularProgress size={24} />}
                </Box>

                {errorMessage && (
                    <Box sx={{ mt: 2 }}>
                        <Alert severity='error'>{errorMessage}</Alert>
                    </Box>
                )}
            </Paper>

            {response?.success && (
                <Paper variant='outlined' sx={{ p: 2 }}>
                    <Alert severity='success' sx={{ mb: 2 }}>
                        Performance test queued.
                    </Alert>

                    <Typography sx={{ fontWeight: 700, mb: 1 }}>
                        Test ID: <span style={{ fontWeight: 600 }}>{response.test_id}</span>
                    </Typography>
                    <Typography sx={{ mb: 2 }}>{response.message}</Typography>

                    <Typography variant='subtitle1' sx={{ fontWeight: 700, mb: 1 }}>
                        Status: {response.status}
                    </Typography>

                    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
                        <Box>
                            <Typography sx={{ fontWeight: 700 }}>Config</Typography>
                            <Typography>users: {response.config?.users}</Typography>
                            <Typography>spawn_rate: {response.config?.spawn_rate}</Typography>
                            <Typography>target: {response.config?.target}</Typography>
                            <Typography>dataset_size: {response.config?.dataset_size}</Typography>
                        </Box>

                        <Box>
                            <Typography sx={{ fontWeight: 700, mb: 1 }}>Endpoints</Typography>
                            {response.endpoints?.status && (
                                <Typography sx={{ mb: 0.5 }}>
                                    <a href={`${apiOrigin}${response.endpoints.status}`} target='_blank' rel='noreferrer'>
                                        Test Status
                                    </a>
                                </Typography>
                            )}
                            {response.endpoints?.results && (
                                <Typography sx={{ mb: 0.5 }}>
                                    <a href={`${apiOrigin}${response.endpoints.results}`} target='_blank' rel='noreferrer'>
                                        Test Results
                                    </a>
                                </Typography>
                            )}
                            {response.endpoints?.download_html && (
                                <Typography sx={{ mb: 0.5 }}>
                                    <a href={`${apiOrigin}${response.endpoints.download_html}`} target='_blank' rel='noreferrer'>
                                        Download HTML Report
                                    </a>
                                </Typography>
                            )}
                            {response.endpoints?.download_csv && (
                                <Typography>
                                    <a href={`${apiOrigin}${response.endpoints.download_csv}`} target='_blank' rel='noreferrer'>
                                        Download CSV Report
                                    </a>
                                </Typography>
                            )}
                        </Box>
                    </Box>
                </Paper>
            )}

            <Box sx={{ height: 10 }} />

            <Paper variant='outlined' sx={{ p: 2 }}>
                <Typography variant='subtitle1' sx={{ fontWeight: 700, mb: 1 }}>
                    Test Status
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, mb: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                    <Button
                        variant='contained'
                        color='secondary'
                        onClick={onGetStatus}
                        disabled={isFetchingStatus || !testId}
                    >
                        {isFetchingStatus ? 'Fetching...' : 'Get Status'}
                    </Button>
                    <Tooltip title='Refresh status'>
                        <span>
                            <IconButton
                                color='secondary'
                                onClick={onGetStatus}
                                disabled={isFetchingStatus || !testId}
                                aria-label='Refresh status'
                                size='medium'
                            >
                                <RefreshIcon />
                            </IconButton>
                        </span>
                    </Tooltip>
                    {isFetchingStatus && <CircularProgress size={24} />}
                </Box>

                {statusErrorMessage && <Alert severity='error'>{statusErrorMessage}</Alert>}

                {statusResponse && (
                    <Box>
                        <Alert severity='success' sx={{ mb: 2 }}>
                            Status: {statusResponse.status}
                        </Alert>

                        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
                            <Box>
                                <Typography sx={{ fontWeight: 700 }}>Overview</Typography>
                                <Typography>created_at: {statusResponse.created_at}</Typography>
                                <Typography>start_time: {statusResponse.start_time}</Typography>
                                <Typography>end_time: {statusResponse.end_time}</Typography>
                                <Typography>state: {statusResponse.state}</Typography>
                                <Typography>progress: {statusResponse.progress}%</Typography>
                                <Typography>mode: {statusResponse.mode}</Typography>
                                <Typography>swarm_started: {String(statusResponse.swarm_started)}</Typography>
                                <Typography>data_points: {statusResponse.data_points}</Typography>
                                <Typography>completed_requests: {statusResponse.completed_requests}</Typography>
                                <Typography>total_requests: {statusResponse.total_requests}</Typography>
                            </Box>

                            <Box>
                                <Typography sx={{ fontWeight: 700 }}>Performance</Typography>
                                <Typography>total_users: {statusResponse.total_users}</Typography>
                                <Typography>current_users: {statusResponse.current_users}</Typography>
                                <Typography>rps: {statusResponse.rps}</Typography>
                                <Typography>error_rate: {statusResponse.error_rate}</Typography>
                                <Typography>elapsed_seconds: {statusResponse.elapsed_seconds}</Typography>
                                <Typography>
                                    quality_metrics.info: {statusResponse.quality_metrics?.info ?? ''}
                                </Typography>
                            </Box>
                        </Box>

                        <Divider sx={{ my: 2 }} />

                        <Typography sx={{ fontWeight: 700, mb: 1 }}>Config</Typography>
                        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 1 }}>
                            <Typography>host: {String(statusResponse.config?.host ?? '')}</Typography>
                            <Typography>path: {String(statusResponse.config?.path ?? '')}</Typography>
                            <Typography>users: {String(statusResponse.config?.users ?? '')}</Typography>
                            <Typography>spawn_rate: {String(statusResponse.config?.spawn_rate ?? '')}</Typography>
                            <Typography>dataset_size: {String(statusResponse.config?.dataset_size ?? '')}</Typography>
                            <Typography>randomize: {String(statusResponse.config?.randomize ?? '')}</Typography>
                        </Box>

                        {statusResponse.reports?.csv && (
                            <>
                                <Divider sx={{ my: 2 }} />
                                <Typography sx={{ fontWeight: 700, mb: 1 }}>Reports</Typography>
                                <Typography>
                                    <a
                                        href={`${apiOrigin}/${statusResponse.reports.csv}`}
                                        target='_blank'
                                        rel='noreferrer'
                                    >
                                        Download CSV
                                    </a>
                                </Typography>
                            </>
                        )}

                        {statusResponse.final_stats && (
                            <>
                                <Divider sx={{ my: 2 }} />
                                <Typography sx={{ fontWeight: 700, mb: 1 }}>Final Stats (summary)</Typography>
                                <Typography>
                                    fail_ratio: {String((statusResponse.final_stats as any)?.fail_ratio ?? '')}
                                </Typography>
                                <Typography>
                                    state: {String((statusResponse.final_stats as any)?.state ?? '')}
                                </Typography>
                                <Typography>
                                    errors_count:{' '}
                                    {Array.isArray((statusResponse.final_stats as any)?.errors)
                                        ? (statusResponse.final_stats as any).errors.length
                                        : 0}
                                </Typography>
                            </>
                        )}

                        <Box sx={{ mt: 2 }}>
                            <Accordion>
                                <AccordionSummary>
                                    <Typography sx={{ fontWeight: 700 }}>Raw response</Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    <Box
                                        component='pre'
                                        sx={{
                                            m: 0,
                                            whiteSpace: 'pre-wrap',
                                            wordBreak: 'break-word',
                                            fontFamily: 'monospace',
                                            fontSize: '12px',
                                            maxHeight: 280,
                                            overflow: 'auto',
                                            backgroundColor: 'rgba(0,0,0,0.03)',
                                            borderRadius: 1,
                                            p: 1,
                                        }}
                                    >
                                        {JSON.stringify(statusResponse, null, 2)}
                                    </Box>
                                </AccordionDetails>
                            </Accordion>
                        </Box>
                    </Box>
                )}
            </Paper>

            <Paper variant='outlined' sx={{ p: 2 }}>
                <Typography variant='subtitle1' sx={{ fontWeight: 700, mb: 1 }}>
                    Test results
                </Typography>
                <Typography variant='body2' color='text.secondary' sx={{ mb: 2 }}>
                    GET{' '}
                    <Box component='span' sx={{ fontFamily: 'monospace', fontSize: '0.85em' }}>
                        {TEST_RESULTS_BASE}/{testId || '…'}
                    </Box>
                    . When the swarm is {SWARM_STATE.STOPPED}, results are polled every {TEST_RESULTS_POLL_MS / 1000}s
                    while <Box component='span' sx={{ fontFamily: 'monospace' }}>status</Box> is{' '}
                    <Box component='span' sx={{ fontFamily: 'monospace' }}>&quot;running&quot;</Box>, then quality
                    metrics HTML loads automatically.
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2, alignItems: 'center' }}>
                    <Button
                        variant='outlined'
                        onClick={onGetTestResult}
                        disabled={!testId || testResultsLoading}
                    >
                        {testResultsLoading && !testResultsPolling ? 'Loading…' : 'Get Test Result'}
                    </Button>
                    <Button
                        variant='outlined'
                        onClick={onGetQualityMetricsHtml}
                        disabled={!testId || qualityMetricsLoading}
                    >
                        {qualityMetricsLoading ? 'Loading…' : 'Get Quality Metrics HTML'}
                    </Button>
                </Box>

                {testResultsPolling && (
                    <Alert severity='info' sx={{ mb: 2 }}>
                        Waiting for test results: <Box component='span' sx={{ fontFamily: 'monospace' }}>status</Box>{' '}
                        is still &quot;running&quot; (checking every {TEST_RESULTS_POLL_MS / 1000}s).
                    </Alert>
                )}

                {testResultsError && <Alert severity='error' sx={{ mb: 2 }}>{testResultsError}</Alert>}

                {testResults && (
                    <Box sx={{ mt: 1 }}>
                        <Typography sx={{ fontWeight: 700, mb: 1 }}>
                            Result status:{' '}
                            <Box component='span' sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                                {testResults.status ?? '—'}
                            </Box>
                        </Typography>
                        <Accordion>
                            <AccordionSummary>
                                <Typography sx={{ fontWeight: 700 }}>Raw test results JSON</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                <Box
                                    component='pre'
                                    sx={{
                                        m: 0,
                                        whiteSpace: 'pre-wrap',
                                        wordBreak: 'break-word',
                                        fontFamily: 'monospace',
                                        fontSize: '12px',
                                        maxHeight: 280,
                                        overflow: 'auto',
                                        backgroundColor: 'rgba(0,0,0,0.03)',
                                        borderRadius: 1,
                                        p: 1,
                                    }}
                                >
                                    {JSON.stringify(testResults, null, 2)}
                                </Box>
                            </AccordionDetails>
                        </Accordion>
                    </Box>
                )}
            </Paper>

            <Paper variant='outlined' sx={{ p: 2 }}>
                <Typography variant='subtitle1' sx={{ fontWeight: 700, mb: 1 }}>
                    Quality metrics (HTML preview)
                </Typography>
                <Typography variant='body2' color='text.secondary' sx={{ mb: 2 }}>
                    Loaded from{' '}
                    <Box component='span' sx={{ fontFamily: 'monospace', fontSize: '0.85em' }}>
                        {QUALITY_METRICS_HTML_BASE}/{testId || '…'}
                    </Box>
                    . Fetches automatically after test results finish (when not &quot;running&quot;), or use{' '}
                    <Box component='span' sx={{ fontWeight: 600 }}>Get Quality Metrics HTML</Box> above.
                </Typography>

                {qualityMetricsLoading && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <CircularProgress size={24} />
                        <Typography variant='body2'>Loading HTML…</Typography>
                    </Box>
                )}

                {qualityMetricsError && (
                    <Alert severity='error' sx={{ mb: 2 }}>
                        {qualityMetricsError}
                    </Alert>
                )}

                {!qualityMetricsLoading && !qualityMetricsHtml && (
                    <Alert severity='info'>No HTML loaded yet. Stop the swarm or use Get Quality Metrics HTML.</Alert>
                )}

                {!qualityMetricsLoading && qualityMetricsHtml && (
                    <Box
                        component='iframe'
                        title='Quality metrics HTML'
                        srcDoc={qualityMetricsHtml}
                        sandbox='allow-same-origin'
                        sx={{
                            width: '100%',
                            minHeight: 320,
                            border: 1,
                            borderColor: 'divider',
                            borderRadius: 1,
                            bgcolor: 'background.paper',
                        }}
                    />
                )}
            </Paper>
        </Box>
    );
}

