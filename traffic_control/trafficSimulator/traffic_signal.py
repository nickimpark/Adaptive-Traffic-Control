class TrafficSignal:
    def __init__(self, roads, config={}):
        # Initialize roads
        self.roads = roads
        # Set default configuration
        self.set_default_config()
        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)
        # Calculate properties
        self.init_properties()
        self.traffic_data = [
            [0, 0, 0, 0, 0, 0],  # Person, Bicycle, Car, Motorbike, Bus, Truck
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0]
        ]
        self.vehicles_passed = 0

    def set_default_config(self):
        self.cycle = [(True, False), (False, True)]
        self.fixed_flag = True
        self.adjust_flag = False
        self.cycle_length_1 = 30
        self.cycle_length_2 = 30
        self.slow_distance = 50
        self.slow_factor = 0.4
        self.stop_distance = 15
        self.current_cycle_index = 0
        self.time_off = 0

    def init_properties(self):
        for i in range(len(self.roads)):
            for road in self.roads[i]:
                road.set_traffic_signal(self, i)

    @property
    def current_cycle(self):
        return self.cycle[self.current_cycle_index]
    
    def update(self, sim):
        temp = sim.t - self.time_off
        if self.fixed_flag:
            if (temp > self.cycle_length_1) and (self.current_cycle_index == 0):
                self.time_off = sim.t
                self.current_cycle_index = 1
                temp = 0
                self.fixed_flag = False  # comment this to enable infinite non-adaptive state
                return
            if (temp > self.cycle_length_2) and (self.current_cycle_index == 1):
                self.time_off = sim.t
                self.current_cycle_index = 0
                temp = 0

        if not self.fixed_flag:
            if (temp > self.cycle_length_1) and (self.current_cycle_index == 0):
                # Step 2: 2nd and 4th signals green
                # Number of cars near 2st and 4rd signals
                cars_number_1 = self.traffic_data[1][2] + 2 * (self.traffic_data[1][4] + self.traffic_data[1][5])
                cars_number_3 = self.traffic_data[3][2] + 2 * (self.traffic_data[3][4] + self.traffic_data[3][5])
                cars_number_13 = (cars_number_1 + cars_number_3) / 2
                # Decision about the duration of green phase (2 and 4)
                if cars_number_13 < 5:
                    self.cycle_length_2 = 20
                elif (cars_number_13 >= 5) and (cars_number_13 < 10):
                    self.cycle_length_2 = 30
                elif (cars_number_13 >= 10) and (cars_number_13 < 15):
                    self.cycle_length_2 = 45
                elif (cars_number_13 >= 15) and (cars_number_13 <= 20):
                    self.cycle_length_2 = 60
                elif cars_number_13 > 20:
                    self.cycle_length_2 = 75

                self.time_off = sim.t
                self.current_cycle_index = 1
                self.adjust_flag = True
                temp = 0

            if (temp > self.cycle_length_2 // 2) and (self.current_cycle_index == 1) and (self.adjust_flag):
                # Data about 1st and 3rd signals
                cars_number_0 = self.traffic_data[0][2] + 2 * (self.traffic_data[0][4] + self.traffic_data[0][5])
                cars_number_2 = self.traffic_data[2][2] + 2 * (self.traffic_data[2][4] + self.traffic_data[2][5])
                cars_number_02 = (cars_number_0 + cars_number_2) / 2
                # Data about 2st and 4rd signals
                cars_number_1 = self.traffic_data[1][2] + 2 * (self.traffic_data[1][4] + self.traffic_data[1][5])
                cars_number_3 = self.traffic_data[3][2] + 2 * (self.traffic_data[3][4] + self.traffic_data[3][5])
                cars_number_13 = (cars_number_1 + cars_number_3) / 2
                # Adjustment if more cars on the second road
                if (cars_number_02 >= 10) and (cars_number_13 < 5):
                    self.cycle_length_2 /= 1.5
                # Adjustment if more cars on this road
                if (cars_number_02 < 5) and (cars_number_13 >= 10):
                    self.cycle_length_2 *= 1.5
                self.adjust_flag = False

            if (temp > self.cycle_length_2) and (self.current_cycle_index == 1):
                # Step 1: 1st and 3rd signals green
                # Number of cars near 1st and 3rd signals
                cars_number_0 = self.traffic_data[0][2] + 2 * (self.traffic_data[0][4] + self.traffic_data[0][5])
                cars_number_2 = self.traffic_data[2][2] + 2 * (self.traffic_data[2][4] + self.traffic_data[2][5])
                cars_number_02 = (cars_number_0 + cars_number_2) / 2
                # Decision about the duration of green phase (1 and 3)
                if cars_number_02 < 5:
                    self.cycle_length_1 = 15
                elif (cars_number_02 >= 5) and (cars_number_02 < 10):
                    self.cycle_length_1 = 30
                elif (cars_number_02 >= 10) and (cars_number_02 < 15):
                    self.cycle_length_1 = 45
                elif (cars_number_02 >= 15) and (cars_number_02 <= 20):
                    self.cycle_length_1 = 60
                elif cars_number_02 > 20:
                    self.cycle_length_1 = 75

                self.time_off = sim.t
                self.current_cycle_index = 0
                self.adjust_flag = True
                temp = 0

            if (temp > self.cycle_length_1 // 2) and (self.current_cycle_index == 0) and (self.adjust_flag):
                # Data about 1st and 3rd signals
                cars_number_0 = self.traffic_data[0][2] + 2 * (self.traffic_data[0][4] + self.traffic_data[0][5])
                cars_number_2 = self.traffic_data[2][2] + 2 * (self.traffic_data[2][4] + self.traffic_data[2][5])
                cars_number_02 = (cars_number_0 + cars_number_2) / 2
                # Data about 2st and 4rd signals
                cars_number_1 = self.traffic_data[1][2] + 2 * (self.traffic_data[1][4] + self.traffic_data[1][5])
                cars_number_3 = self.traffic_data[3][2] + 2 * (self.traffic_data[3][4] + self.traffic_data[3][5])
                cars_number_13 = (cars_number_1 + cars_number_3) / 2
                # Adjustment if more cars on the second road
                if (cars_number_13 >= 0) and (cars_number_02 < 5):
                    self.cycle_length_1 /= 1.5
                # Adjustment if more cars on this road
                if (cars_number_13 < 5) and (cars_number_02 >= 0):
                    self.cycle_length_1 *= 1.5
                self.adjust_flag = False
