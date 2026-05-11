from hashlib import md5

# message
#m = "1JodieTucker37"

# identity
#i1 = 3231265
#i2 = 5342532
#i3 = 4526377

i1 = 126
i2 = 127
i3 = 128

# pkg
#p = 307699126915021078949717556805305347641
#q = 286189067004968539490940912607240844261
p = 1004162036461488639338597000466705179253226703
q = 950133741151267522116252385927940618264103623


# pkg side

n = p * q
print(f"n: {n}")

phi_n = (p - 1) * (q - 1)
print(f"phi_n: {phi_n}")

#e = 71
e = 973028207197278907211

d = pow(e, -1, phi_n)
print(f"d: {d}")

# pkg side end

# generate secret key for each inventory
# gn = in^d mod n

g1 = pow(i1, d, n)
print(f"g1: {g1}")

g2 = pow(i2, d, n)
print(f"g2: {g2}")

g3 = pow(i3, d, n)
print(f"g3: {g3}")

#r1 = 124524
#r2 = 117623
#r3 = 156253

r1 = 621
r2 = 721
r3 = 821


# generate partial try:
# tj = rj^e mod n

t1 = pow(r1, e, n)
print(f"t1: {t1}")

t2 = pow(r2, e, n)
print(f"t2: {t2}")

t3 = pow(r3, e, n)
print(f"t3: {t3}")

t = t1*t2*t3 % n
print(f"t: {t}")

c_m = str(t) + m

h_m = md5(c_m.encode()).hexdigest()
print(f"h_m: {h_m}")

# decimal
int_cm = int(h_m, 16)
print(f"int_cm: {int_cm}")

# each inv sign
# si = gi*ri^h(t,m) mod n
# si_1 = gi mod n
# si_2 = r1 ^ h(t, m) mod n

s1_1 = g1 % n
s1_2 = pow(r1, int_cm, n)
s1 = s1_1 * s1_2 % n
print(f"s1: {s1}")

s2_1 = g2 % n
s2_2 = pow(r2, int_cm, n)
s2 = s2_1 * s2_2 % n
print(f"s2: {s2}")

s3_1 = g3 % n
s3_2 = pow(r3, int_cm, n)
s3 = s3_1 * s3_2 % n
print(f"s3: {s3}")

s = s1*s2*s3 % n
print(f"s: {s}")


# partial verification
# s^e mod n = PHI ij * t ^ h(t, m) mod n

v1 = pow(s, e, n)

v2_1 = i1 * i2 * i3 % n
v2_2 = pow(t, int_cm, n)
v2 = v2_1 * v2_2 % n

print("Verification " + ("success" if v1 == v2 else "failed"))