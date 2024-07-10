total_pixels = 535

pixels_list = [18]

percentages_raw = []
for pixels in pixels_list:
    percentages_raw.append(round((pixels) / total_pixels * 0.6, 2))

# total = sum(percentages_raw)

# if total > 100: 
#     excess = total - 100
#     diff = excess / len(pixels_list)

#     percentages = []
#     for percentage in percentages_raw: 
#         percentages.append(round(percentage - diff, 1))

#     print(percentages) 
#     print(sum(percentages))

print(percentages_raw) 
print(sum(percentages_raw))