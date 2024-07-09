import subprocess
import re
import os
import numpy as np

FFMPEG_BASE_FOLDER =           os.getenv('FFMPEG_BASE_FOLDER', None)
SUDO_PWD =                     os.getenv('SUDO_PWD', None)
FILENAME_TO_CONVERT =          os.getenv('FILENAME_TO_CONVERT', None)
OUTPUT_FILE =                  os.getenv('OUTPUT_FILE', None)
TEST_SIZE =                    os.getenv('TEST_SIZE', None)

class MassExecution:
    def __init__(self):
        self.base_folder = FFMPEG_BASE_FOLDER
        self.sudo_pwd = SUDO_PWD
        self.filename_to_convert = FILENAME_TO_CONVERT
        self.output_file = OUTPUT_FILE
        self.test_size = int(TEST_SIZE)
        self._results = []

    def commands_runner(self, command):
        subprocess.run(command, shell=True, text=True)

    def create_folder(self):
        command = f'mkdir {self.base_folder}/prof_results'
        self.commands_runner(command)

    def delete_output(self):
        command = f'echo {self.sudo_pwd} | rm -f {self.output_file}'
        self.commands_runner(command)

    def execute_profiling(self, id):
        command = f'echo {self.sudo_pwd} | sudo -S perf stat -o {self.base_folder}/prof_results/ffmpeg_prof_{id}.txt -- {self.base_folder}/ffmpeg_g -i {self.filename_to_convert} -c:a aac -b:a 192k {self.output_file}'
        print(command)
        self.commands_runner(command)

    def delete_report_folder(self):
        command = f'echo {self.sudo_pwd} | sudo -S rm -rf {self.base_folder}/prof_results'
        self.commands_runner(command)

    def execute_test(self):
        """ Gera os profiling reports """
        self.create_folder()
        for i in range(0, self.test_size):            
            self.execute_profiling(i)
            self.delete_output()

    def parse_single_string(self, content):
        pattern = r'(\d.*\d)\s+cycles'
        match = re.search(pattern, content)
        if match:
            # cycles = match.group(1).replace('.', '')
            cycles = int(match.group(1).replace('.', ''))
            return cycles


    def gather_results(self):
        for filename in os.listdir(f'{self.base_folder}/prof_results'):
            filepath = os.path.join(f'{self.base_folder}/prof_results', filename)
            with open(filepath, 'r') as file:
                self._results.append(self.parse_single_string(file.read()))

    @property
    def results(self):
        return self._results
    
    def get_mean(self):
        return np.mean(self._results)


def main():
    first_exec = MassExecution()
    first_exec.execute_test()
    first_exec.gather_results()    

    print(first_exec.results)
    print(f"A média é {first_exec.get_mean()}")

    # first_exec.delete_report_folder()

if __name__ == "__main__":
    main()
