def measure_period(self, trace:list[int]) -> float:
    sampling_period:float = 1/self.specs['fs']
    period_start:bool = False
    period_cycle:bool = False
    measured_period:float = 0
    for sample in trace:
        if(sample and not period_start):
            period_start = True
        elif(not sample and period_start and not period_cycle):
            period_cycle = True 
        elif(sample and period_start and period_cycle):
            return measured_period
        if(period_start):
            measured_period += sampling_period
    return None
