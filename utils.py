from pykalman import KalmanFilter
import numpy as np
import matplotlib.pyplot as plt
import time
import pdb


class kalmanFilter:
    def __init__(self, measurements):
        self.measurements = measurements

        self.initial_state_mean = [self.measurements[0, 0],
                                   0,
                                   self.measurements[0, 1],
                                   0]

        self.transition_matrix = [[1, 1, 0, 0],
                                  [0, 1, 0, 0],
                                  [0, 0, 1, 1],
                                  [0, 0, 0, 1]]

        self.observation_matrix = [[1, 0, 0, 0],
                                   [0, 0, 1, 0]]

        self.kf1 = KalmanFilter(transition_matrices=self.transition_matrix,
                                observation_matrices=self.observation_matrix,
                                initial_state_mean=self.initial_state_mean)

        self.kf1 = self.kf1.em(measurements, n_iter=10)
        n_real_time = 3

        kf3 = KalmanFilter(transition_matrices=self.transition_matrix,
                           observation_matrices=self.observation_matrix,
                           initial_state_mean=self.initial_state_mean,
                           observation_covariance=10 * self.kf1.observation_covariance,
                           em_vars=['transition_covariance', 'initial_state_covariance'])

        self.kf3 = self.kf3.em(measurements[:-n_real_time, :], n_iter=5)
        (filtered_state_means, filtered_state_covariances) = kf3.filter(measurements[:-n_real_time, :])

        x_now = filtered_state_means[-1, :]
        P_now = filtered_state_covariances[-1, :]
        x_new = np.zeros((n_real_time, filtered_state_means.shape[1]))
        i = 0

        for measurement in measurements[-n_real_time:, :]:
            time_before = time.time()
            (x_now, P_now) = kf3.filter_update(filtered_state_mean=x_now,
                                               filtered_state_covariance=P_now,
                                               observation=measurement)
            print("Time to update kf3: %s seconds" % (time.time() - time_before))
            x_new[i, :] = x_now
            i = i + 1

    def smooth_res(self):
        (smoothed_state_means, smoothed_state_covariances) = self.kf1.smooth(measurements)
        return (smoothed_state_means, smoothed_state_covariances)


if __name__ == "__main__":
    measurements = np.asarray(
        [(399, 293), (403, 299), (409, 308), (416, 315), (418, 318), (420, 323), (429, 326), (423, 328), (429, 334),
         (431, 337), (433, 342), (434, 352), (434, 349), (433, 350), (431, 350), (430, 349), (428, 347), (427, 345),
         (425, 341), (429, 338), (431, 328), (410, 313), (406, 306), (402, 299), (397, 291), (391, 294), (376, 270),
         (372, 272), (351, 248), (336, 244), (327, 236), (307, 220)])
    KF = kalmanFilter(measurements)
    smoothed_state_means, smoothed_state_covariances = KF.smooth_res()
    # pdb.set_trace()
    plt.figure(1)
    times = range(measurements.shape[0])
    plt.plot(times, measurements[:, 0], 'bo',
             times, measurements[:, 1], 'ro',
             times, smoothed_state_means[:, 0], 'b--',
             times, smoothed_state_means[:, 2], 'r--', )
    plt.show()
