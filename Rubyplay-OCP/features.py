from datetime import (
    datetime,
    timedelta,
)

from typing import (
    List,
    Optional,
    Union,
)

import numpy as np
import pandas as pd

from sklearn.preprocessing import OneHotEncoder


ONE_HOT_COLUMNS = ('currencyCode', 'deviceType', 'gameId')


def _update_dict(d: dict, other_d: dict) -> dict:
    """Update a given dictionary with keys and values from the other one,
    preventing keys collision.
    """
    keys = set(d.keys())
    other_keys = set(other_d.keys())
    intersection = keys & other_keys
    assert len(intersection) == 0, f'There are common features: {intersection}'
    d.update(other_d)
    return d


def most_common_value(xs):
    assert len(xs) > 0

    return next(iter(xs))


def one_hot_features(df, one_hot_encoder, one_hot_columns):
    values = list()

    for column in one_hot_columns:
        values.append(most_common_value(df[column]))

    features = one_hot_encoder.transform([values])[0]
    features = dict(zip(one_hot_encoder.get_feature_names(one_hot_columns),
                        features))
    return features


def timestamp_features(timestamp, prefix):
    d = dict()

    timestamp = datetime.fromtimestamp(timestamp)

    d['weekday'] = timestamp.weekday()
    d['hour'] = timestamp.hour
    d['minute'] = timestamp.minute

    return {'{}_{}'.format(prefix, k): v for k, v in d.items()}


def events_rate_features(ts_diffs, prefix):
    stats = pd.Series(ts_diffs).describe().to_dict()
    stats['log_count'] = np.log(stats['count'])
    return {'{}_{}'.format(prefix, k): v for k, v in stats.items()}


def session_timing_features(timestamps):
    timestamps = pd.Series(timestamps)
    ts_diffs = timestamps.diff().dropna()

    d = dict()

    d['session_duration'] = timestamps.iloc[-1] - timestamps.iloc[0]
    _update_dict(d, events_rate_features(ts_diffs, 'session_events_rate'))

    index = timestamps >= timestamps.iloc[-1] - timedelta(minutes=5).seconds
    _update_dict(d, events_rate_features(ts_diffs[index],
                                         'last_5_min_events_rate'))

    index = timestamps >= timestamps.iloc[-1] - timedelta(minutes=30).seconds
    _update_dict(d, events_rate_features(ts_diffs[index],
                                         'last_30_min_events_rate'))

    index = timestamps >= timestamps.iloc[-1] - timedelta(hours=1).seconds
    _update_dict(d, events_rate_features(ts_diffs[index],
                                         'last_1_h_events_rate'))

    return d


def datetime_features(df: pd.DataFrame) -> dict:
    assert df.shape[0] > 1
    d = dict()

    s = df['unix_timestamp']

    _update_dict(d, timestamp_features(s.iloc[0], 'session_start'))
    _update_dict(d, timestamp_features(s.iloc[-1], 'session_end'))
    _update_dict(d, timestamp_features(s.iloc[int(len(s) / 2)], 'session_mid'))
    _update_dict(d, session_timing_features(s))

    return d


def bet_features(df):
    d = df['bet'].describe().to_dict()
    d = {'bet_{}'.format(k): v for k, v in d.items() if k != 'count'}

    last_ts = df['unix_timestamp'].iloc[-1]

    d['bet_total'] = np.sum(df['bet'])
    d['bet_logtotal'] = np.log(d['bet_total'])

    d['bet_free_spins'] = np.sum(df['bet'] == 0)
    d['bet_free_spins_last_5m'] = np.sum(df[df['unix_timestamp'] >=
                                            last_ts - timedelta(minutes=5)
                                            .seconds]['bet'] == 0)
    d['bet_free_spins_last_30m'] = np.sum(df[df['unix_timestamp'] >=
                                             last_ts - timedelta(minutes=30)
                                             .seconds]['bet'] == 0)
    d['bet_free_spins_last_1h'] = np.sum(df[df['unix_timestamp'] >=
                                            last_ts - timedelta(hours=1)
                                            .seconds]['bet'] == 0)

    d['bet_free_spins_rate'] = d['bet_free_spins'] / df.shape[0]
    d['bet_free_spins_rate_last_5m'] = (d['bet_free_spins_last_5m'] /
                                        df.shape[0])
    d['bet_free_spins_rate_last_30m'] = (d['bet_free_spins_last_30m'] /
                                         df.shape[0])
    d['bet_free_spins_rate_last_1h'] = (d['bet_free_spins_last_1h'] /
                                        df.shape[0])

    d['bet_free_spins_last_5m'] = np.sum(df[df['unix_timestamp'] >=
                                            last_ts - timedelta(minutes=5)
                                            .seconds]['bet'] == 0)
    d['bet_free_spins_last_30m'] = np.sum(df[df['unix_timestamp'] >=
                                             last_ts - timedelta(minutes=30)
                                             .seconds]['bet'] == 0)
    d['bet_free_spins_last_1h'] = np.sum(df[df['unix_timestamp'] >=
                                            last_ts - timedelta(hours=1)
                                            .seconds]['bet'] == 0)

    return d


def win_features(df):
    d = df['win'].describe().to_dict()
    d = {'win_{}'.format(k): v for k, v in d.items() if k != 'count'}

    last_ts = df['unix_timestamp'].iloc[-1]

    d['win_total'] = np.sum(df['win'])

    d['win_last_5m'] = np.sum(df[df['unix_timestamp'] >=
                                 last_ts - timedelta(minutes=5)
                                 .seconds]['win'])
    d['win_last_30m'] = np.sum(df[df['unix_timestamp'] >=
                                  last_ts - timedelta(minutes=30)
                                  .seconds]['win'])
    d['win_last_1h'] = np.sum(df[df['unix_timestamp'] >=
                                 last_ts - timedelta(hours=1)
                                 .seconds]['win'])

    d['win_rate'] = np.sum(df['win'] > 0) / df.shape[0]
    d['win_rate_last_5m'] = np.sum(df[df['unix_timestamp'] >=
                                      last_ts - timedelta(minutes=5)
                                      .seconds]['win'] > 0) / df.shape[0]
    d['win_rate_last_30m'] = np.sum(df[df['unix_timestamp'] >=
                                       last_ts - timedelta(minutes=30)
                                       .seconds]['win'] > 0) / df.shape[0]
    d['win_rate_last_1h'] = np.sum(df[df['unix_timestamp'] >=
                                      last_ts - timedelta(hours=1)
                                      .seconds]['win'] > 0) / df.shape[0]

    return d


def balance_features(df):
    def describe(s, hint):
        s = s.describe().to_dict()
        s = {'balance_{}_{}'.format(hint, k): v
             for k, v in s.items() if k != 'count'}
        return s

    last_ts = df['unix_timestamp'].iloc[-1]

    d = dict()
    _update_dict(d, describe(df['balance'], 'all'))
    _update_dict(d, describe(df[df['unix_timestamp'] >=
                                last_ts - timedelta(minutes=5)
                                .seconds]['balance'], 'last_5m'))
    _update_dict(d, describe(df[df['unix_timestamp'] >=
                                last_ts - timedelta(minutes=30)
                                .seconds]['balance'], 'last_30m'))
    _update_dict(d, describe(df[df['unix_timestamp'] >=
                                last_ts - timedelta(hours=1)
                                .seconds]['balance'], 'last_1h'))
    _update_dict(d, {'balance_last': df.iloc[-1]['balance']})

    return d


def last_balance_to_initial_balance_features(df, hint=None) -> dict:
    last_balance = df.iloc[-1]['balance']

    max_idx = min(5, df.shape[0])

    for idx in range(max_idx):
        initial_balance = df.iloc[idx]['balance']

        if initial_balance > 0:
            break

    if initial_balance == 0:
        feature = 0
    else:
        feature = last_balance / initial_balance

    feature_name = 'last_balance_to_initial_balance'

    if hint is not None:
        feature_name += f'_{hint}'

    result = {
        feature_name: feature,
    }

    return result


def lag_after_win_features(df: pd.DataFrame) -> dict:
    df = df.copy()
    df['lag'] = -df['unix_timestamp'].diff(-1)
    lags_after_wins = df.loc[df['win'] > 0, 'lag']
    features = lags_after_wins.describe().fillna(0).to_dict()

    del features['count']

    features = {f'lag_after_win_{k}': v for k, v in features.items()}

    return features


def bet_ups_downs_same_features(df: pd.DataFrame, hint=None) -> dict:
    dynamics = df['bet'].diff().dropna()

    if len(dynamics) == 0:
        ups = 0.0
        downs = 0.0
        same = 1.0
    else:
        denominator = dynamics.shape[0] + 1
        ups = (dynamics > 0).sum() / denominator
        downs = (dynamics < 0).sum() / denominator
        same = (1 + (dynamics == 0).sum()) / denominator

    features = {
        'bet_uds_ups': ups,
        'bet_uds_downs': downs,
        'bet_uds_same': same,
    }

    if hint is not None:
        features = {f'{k}_{hint}': v for k, v in features.items()}

    return features


def win_to_balance_features(df: pd.DataFrame, hint=None) -> dict:
    ddf = df[df['win'] > 0]
    s = (ddf['win'] / ddf['balance']).replace([-np.inf, np.inf], 0)
    features = s.describe().fillna(0).to_dict()

    del features['count']

    features = {f'win_to_balance_{k}': v for k, v in features.items()}

    if hint is not None:
        features = {f'{k}_{hint}': v for k, v in features.items()}

    return features


def bet_to_balance_features(df: pd.DataFrame, hint=None) -> dict:
    ddf = df[df['bet'] > 0]
    s = (ddf['bet'] / ddf['balance']).replace([-np.inf, np.inf], 0)
    features = s.describe().fillna(0).to_dict()

    del features['count']

    features = {f'bet_to_balance_{k}': v for k, v in features.items()}

    if hint is not None:
        features = {f'{k}_{hint}': v for k, v in features.items()}

    return features


def session_features_extension_01(df: pd.DataFrame,
                                  sort: bool = True,
                                  return_df: bool = False) -> dict:
    if sort:
        df = df.sort_values('unix_timestamp')

    d = dict()

    last_30_seconds = df[df['unix_timestamp'] >=
                         df['unix_timestamp'].iloc[-1] - 30]
    last_1_minute = df[df['unix_timestamp'] >=
                       df['unix_timestamp'].iloc[-1] - 60]
    last_5_minutes = df[df['unix_timestamp'] >=
                        df['unix_timestamp'].iloc[-1] - 6 * 60]
    last_30_minutes = df[df['unix_timestamp'] >=
                         df['unix_timestamp'].iloc[-1] - 30 * 60]

    _update_dict(d, last_balance_to_initial_balance_features(df))
    _update_dict(d,
                 last_balance_to_initial_balance_features(last_30_seconds,
                                                          'last_30_seconds'))
    _update_dict(d,
                 last_balance_to_initial_balance_features(last_1_minute,
                                                          'last_1_minute'))
    _update_dict(d,
                 last_balance_to_initial_balance_features(last_5_minutes,
                                                          'last_5_minutes'))
    _update_dict(d,
                 last_balance_to_initial_balance_features(last_30_minutes,
                                                          'last_30_minutes'))
    _update_dict(d, lag_after_win_features(df))

    _update_dict(d, bet_ups_downs_same_features(df))
    _update_dict(d, bet_ups_downs_same_features(last_1_minute,
                                                'last_1_minute'))
    _update_dict(d, bet_ups_downs_same_features(last_5_minutes,
                                                'last_5_minutes'))
    _update_dict(d, bet_ups_downs_same_features(last_30_minutes,
                                                'last_30_minutes'))

    _update_dict(d, win_to_balance_features(df))
    _update_dict(d, win_to_balance_features(last_1_minute,
                                            'last_1_minute'))
    _update_dict(d, win_to_balance_features(last_5_minutes,
                                            'last_5_minutes'))
    _update_dict(d, win_to_balance_features(last_30_minutes,
                                            'last_30_minutes'))

    _update_dict(d, bet_to_balance_features(df))
    _update_dict(d, bet_to_balance_features(last_1_minute,
                                            'last_1_minute'))
    _update_dict(d, bet_to_balance_features(last_5_minutes,
                                            'last_5_minutes'))
    _update_dict(d, bet_to_balance_features(last_30_minutes,
                                            'last_30_minutes'))

    result = pd.Series(d)

    if return_df:
        result = result.to_frame().T

    return result


def session_features(
        df: pd.DataFrame,
        one_hot_encoder: OneHotEncoder,
        one_hot_columns: List[str] = ONE_HOT_COLUMNS,
        return_df: bool = False,
        extensions: Optional[List[str]] = None,
        sort: bool = True) -> Union[pd.Series, pd.DataFrame, None]:
    d = dict()

    if sort:
        df = df.sort_values('unix_timestamp')

    _update_dict(d, one_hot_features(df, one_hot_encoder, one_hot_columns))
    _update_dict(d, datetime_features(df))
    _update_dict(d, bet_features(df))
    _update_dict(d, win_features(df))
    _update_dict(d, balance_features(df))

    if extensions:
        for extension in extensions:
            features_fn_name = f'session_features_{extension}'
            features_fn = globals().get(features_fn_name, None)

            if not features_fn:
                print(f'[WARN] Function cannot be found: {features_fn_name}')
                continue

            _update_dict(d, features_fn(df, sort=sort).to_dict())

    result = pd.Series(d)

    if return_df:
        result = result.to_frame().T

    return result


def _get_last_win_ts(df: pd.DataFrame) -> int:
    wins_tss = df[df['win'] > 0]['unix_timestamp']

    if wins_tss.shape[0] > 0:
        last_win_ts = wins_tss.iloc[-1] + 1
    else:
        last_win_ts = df['unix_timestamp'].max()

    return last_win_ts


def session_features_endsession(
        df: pd.DataFrame,
        one_hot_encoder: OneHotEncoder,
        one_hot_columns: List[str],
        min_events: Optional[int] = 32,
        last_n_seconds: Optional[int] = None,
        since_last_win: bool = False,
        columns: Optional[List[str]] = None,
        include_ids: bool = False) -> Union[pd.DataFrame, None]:
    """Return features for all the windows in the user session, calculated
    according to arguments.

    In case if `last_n_seconds` is given (an integral number of seconds), the
    number of datapoints to be calculated is at most the number of events
    within the given number of seconds at the session end.

    In case if `since_last_win` is not `False`, the number of events is at most
    the number of events since the last win until the end of session.

    User should pass either `last_n_seconds` or `since_last_win`.

    Arguments:
        df: A dataframe of a session.
        one_hot_encoder: A one-hot encoder to transform categorical features.
        one_hot_columns: A list of columns to be transformed with one-hot
            encoder.
        min_events: A minimum number of events in a (sub)session to calculate
            features for. If `None`, there's no lower limit.
        last_n_seconds: [optional] A time window (in seconds) at the end of
            session to reckon events in as the end of session.
        since_last_win: [optional] A boolean flag, which denotes that the time
            window at the end of session. All the events from this window is
            reckoned as the last event in a session.
        columns: A list of columns to be returned.

    Returns:
        A DataFrame or `None`. If columns are passed, but no data points are
        calculated, empty DataFrame is returned with all the requested columns.
    """
    assert not (last_n_seconds is not None and since_last_win), \
        ('Either of `last_n_seconds` or `since_last_win` '
         'should be passed, not both')
    assert not df.isna().any().any(), ('None of values are expected to '
                                       'be missing')

    df = df.sort_values('unix_timestamp')
    last_event_ts = df['unix_timestamp'].max()

    if since_last_win:
        last_n_seconds = last_event_ts - _get_last_win_ts(df)

    if not last_n_seconds:
        last_n_seconds = 0

    mask = df['unix_timestamp'] >= last_event_ts - last_n_seconds
    events_timestamps = df[mask]['unix_timestamp']

    if min_events is None:
        min_events = 0

    rows = list()

    for ts in events_timestamps:
        ddf = df[df['unix_timestamp'] <= ts]

        if ddf.shape[0] < min_events:
            continue

        features = session_features(ddf, one_hot_encoder, one_hot_columns)
        features = features.fillna(0)
        rows.append(features)

    if len(rows) > 0:
        features = pd.concat(rows, axis=1, copy=False, ignore_index=True).T
    else:
        if columns:
            features = pd.DataFrame(columns=columns, dtype=np.float32)
        else:
            features = None

    if isinstance(features, pd.DataFrame):
        if columns:
            df_cols = set(features.columns)
            cols = set(columns)
            assert cols == df_cols

            features = features[columns]

        if include_ids:
            first_row = df.iloc[0]
            features['playerId'] = first_row['playerId']
            features['gameSessionId'] = first_row['gameSessionId']

    return features


def session_features_n_second_half(
        df: pd.DataFrame,
        one_hot_encoder: OneHotEncoder,
        one_hot_columns: List[str],
        min_events: int = 32,
        n: int = 10,
        columns: Optional[List[str]] = None,
        include_ids: bool = False,
        extensions: Optional[List[str]] = None,
        include_timestamp: bool = False) -> pd.DataFrame:
    """Collect at most N datapoints from a given session
    """
    df = df.sort_values('unix_timestamp')

    win_balance_nan_index = df[(df['win'] > 0) & df['balance'].isna()].index
    df['balance'] = df['balance'].fillna(method='ffill')
    df.loc[win_balance_nan_index, 'balance'] += df.loc[win_balance_nan_index,
                                                       'win']

    split_point = df.shape[0] // 2
    step = max(1, split_point // n)
    last_index = max(split_point, df.shape[0] - step * n)
    indices = reversed(range(df.shape[0], last_index, -step))

    rows = list()

    for idx in indices:
        if idx < min_events:
            continue

        features = session_features(df.iloc[:idx],
                                    one_hot_encoder=one_hot_encoder,
                                    one_hot_columns=one_hot_columns,
                                    sort=False,
                                    extensions=extensions)

        if include_timestamp:
            features['unix_timestamp'] = df.iloc[idx - 1]['unix_timestamp']

        rows.append(features)

    if len(rows) > 0:
        features = pd.concat(rows, axis=1, copy=False, ignore_index=True).T
    else:
        if columns:
            features = pd.DataFrame(columns=columns, dtype=np.float32)
        else:
            features = None

    if isinstance(features, pd.DataFrame):
        if columns:
            df_cols = set(features.columns)
            cols = set(columns)
            assert cols == df_cols, (f'Missing expected columns: '
                                     f'{cols - df_cols}, excess columns: '
                                     f'{df_cols - cols}')

            features = features[columns]

        if include_ids:
            first_row = df.iloc[0]
            features['playerId'] = first_row['playerId']
            features['gameSessionId'] = first_row['gameSessionId']

    return features
