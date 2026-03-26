import {
    Alert,
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Box,
    Button,
    CircularProgress,
    Divider,
    Paper,
    TextField,
    Typography,
} from '@mui/material';
import { useMemo, useState } from 'react';

const API_URL = 'http://34.71.3.151/start-test';
const STATUS_API_URL = 'http://34.71.3.151/test-status';

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
    const [authorization, setAuthorization] = useState<string>('');
    const [authorizationError, setAuthorizationError] = useState(false);

    // Keep these as separate fields so you can see/edit each payload property directly.
    const [truthCol, setTruthCol] = useState('');
    const [predCol, setPredCol] = useState('');
    const [severityCol, setSeverityCol] = useState('');
    const [nonEventValue, setNonEventValue] = useState('');
    const [nonAlertValue, setNonAlertValue] = useState('');
    const [alertValue, setAlertValue] = useState('');
    const [criticalLevel, setCriticalLevel] = useState('');

    const [qualityTestsJson, setQualityTestsJson] = useState('[]');

    const [datasetId, setDatasetId] = useState('1');
    const [inputName, setInputName] = useState('TEXT');
    const [inputDatatype, setInputDatatype] = useState('BYTES');
    const [shape0, setShape0] = useState<number>(1);
    const [shape1, setShape1] = useState<number>(1);
    const [inputDataJsonString, setInputDataJsonString] = useState(
        '{"window_title": "Google search", "org_type": "Primary", "capture": "Where can I buy ice cream?", "capture_id": "123"}',
    );

    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [response, setResponse] = useState<StartTestResponse | null>(null);

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

    const apiOrigin = useMemo(() => {
        try {
            return new URL(API_URL).origin;
        } catch {
            return '';
        }
    }, []);

    const submitDisabled = isSubmitting || !testId || !host || !path;

    const buildPayload = () => {
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
            dataset: [
                {
                    id: datasetId,
                    inputs: [
                        {
                            name: inputName,
                            datatype: inputDatatype,
                            shape: [shape0, shape1],
                            data: [inputDataJsonString],
                        },
                    ],
                },
            ],
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
        setIsSubmitting(true);
        try {
            const payload = buildPayload();
            const res = await fetch(API_URL, {
                method: 'POST',
                headers: { 'content-type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = (await res.json()) as StartTestResponse;
            setResponse(data);

            if (!data?.success) {
                setErrorMessage(data?.message || 'Request failed');
            }
        } catch (err) {
            setErrorMessage(err instanceof Error ? err.message : 'Request failed');
        } finally {
            setIsSubmitting(false);
        }
    };

    const onGetStatus = async () => {
        if (!testId) return;

        setStatusErrorMessage(null);
        setStatusResponse(null);
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
                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
                    <TextField label='dataset[0].id' value={datasetId} onChange={e => setDatasetId(e.target.value)} />
                    <TextField label='inputs[0].name' value={inputName} onChange={e => setInputName(e.target.value)} />
                    <TextField
                        label='inputs[0].datatype'
                        value={inputDatatype}
                        onChange={e => setInputDatatype(e.target.value)}
                    />
                    <TextField
                        label='inputs[0].shape[0]'
                        type='number'
                        value={shape0}
                        onChange={e => setShape0(Number(e.target.value))}
                    />
                    <TextField
                        label='inputs[0].shape[1]'
                        type='number'
                        value={shape1}
                        onChange={e => setShape1(Number(e.target.value))}
                    />
                    <TextField
                        label='inputs[0].data[0] (JSON string)'
                        value={inputDataJsonString}
                        onChange={e => setInputDataJsonString(e.target.value)}
                        multiline
                        minRows={3}
                        fullWidth
                        sx={{ gridColumn: { xs: '1 / -1', md: 'span 2' } }}
                    />
                </Box>

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

                <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
                    <Button
                        variant='contained'
                        color='secondary'
                        onClick={onGetStatus}
                        disabled={isFetchingStatus || !testId}
                    >
                        {isFetchingStatus ? 'Fetching...' : 'Get Status'}
                    </Button>
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
        </Box>
    );
}

