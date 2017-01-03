def meteor_trajectory(position, coefficients, side_factor):
    position[0] += side_factor
    position[1] = coefficients[0] * position[0] + coefficients[1]



