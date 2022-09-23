from datetime import datetime


class ResultsLogger:
    def __init__(self, logfile_path):
        self.logfile_path = logfile_path
        self.__write_header()

    def __write_header(self):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with open(self.logfile_path, 'a') as f:
            f.write(f'*** A New Processing Batch Has Started At: {now} ***\n')

    def log_acquisition_rate_statistics(self, acquisition_rates, acquisition_mean, acquisition_std_dev):
        for index in range(len(acquisition_rates)):
            acquisition_rates[index] = f'{acquisition_rates[index]:.2f}'

        with open(self.logfile_path, 'a') as f:
            f.write(f'\n*** Rate Acquisition Statistics ***\n')
            f.write(f'Acquisition rates: {acquisition_rates}\n')
            f.write(f'Mean acquisition rate: {acquisition_mean:.2f} vectors/second.\n')
            f.write(f'Standard deviation is: {acquisition_std_dev:.2f}\n')

    def log_matrix_statistics(self, mean, std_dev):
        with open(self.logfile_path, 'a') as f:
            f.write(f'\n*** Matrix Statistics ***\n')
            f.write(f'Matrix mean: {mean:.2f}.\n')
            f.write(f'Standard deviation is: {std_dev:.2f}.\n')
