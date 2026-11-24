# Full loop: night car parks, 43 photos (2026-11-20)

43 photos, 86 bays. Both models trained on public data only. Small sample: indicative only.

## 1. Occupancy (majority vote of the 3 final CNN seeds)

| light | bays | correct | accuracy | false_alarms | missed_cars |
|---|---|---|---|---|---|
| all | 86 | 60 | 0.698 | 20 of 46 empty | 6 of 40 occupied |
| night | 86 | 60 | 0.698 | 20 of 46 empty | 6 of 40 occupied |

| photo | light | bay | truth | p_s42 | p_s43 | p_s44 | pred | correct |
|---|---|---|---|---|---|---|---|---|
| IMG_1821 | night | left | 0 | 0.038 | 0.018 | 0.005 | 0 | True |
| IMG_1821 | night | right | 0 | 0.461 | 0.108 | 0.016 | 0 | True |
| IMG_1822 | night | left | 0 | 0.04 | 0.013 | 0.001 | 0 | True |
| IMG_1822 | night | right | 0 | 0.006 | 0.0 | 0.001 | 0 | True |
| IMG_1823 | night | left | 0 | 0.395 | 0.834 | 0.896 | 1 | False |
| IMG_1823 | night | right | 0 | 0.117 | 0.409 | 0.785 | 0 | True |
| IMG_1824 | night | left | 0 | 0.982 | 0.927 | 0.834 | 1 | False |
| IMG_1824 | night | right | 0 | 0.008 | 0.239 | 0.024 | 0 | True |
| IMG_1825 | night | left | 0 | 0.875 | 0.525 | 0.653 | 1 | False |
| IMG_1825 | night | right | 0 | 0.993 | 0.95 | 0.839 | 1 | False |
| IMG_1826 | night | left | 0 | 0.013 | 0.075 | 0.003 | 0 | True |
| IMG_1826 | night | right | 0 | 0.201 | 0.258 | 0.046 | 0 | True |
| IMG_1827 | night | left | 0 | 0.029 | 0.274 | 0.004 | 0 | True |
| IMG_1827 | night | right | 0 | 0.936 | 0.577 | 0.58 | 1 | False |
| IMG_1828 | night | left | 0 | 0.001 | 0.32 | 0.121 | 0 | True |
| IMG_1828 | night | right | 0 | 0.03 | 0.615 | 0.445 | 1 | False |
| IMG_1829 | night | left | 0 | 0.283 | 0.141 | 0.643 | 0 | True |
| IMG_1829 | night | right | 0 | 0.04 | 0.347 | 0.373 | 0 | True |
| IMG_1830 | night | left | 0 | 0.005 | 0.091 | 0.573 | 0 | True |
| IMG_1830 | night | right | 0 | 0.009 | 0.109 | 0.281 | 0 | True |
| IMG_1831 | night | left | 0 | 0.993 | 0.984 | 0.829 | 1 | False |
| IMG_1831 | night | right | 0 | 0.732 | 0.647 | 0.891 | 1 | False |
| IMG_1832 | night | left | 0 | 0.829 | 0.909 | 0.676 | 1 | False |
| IMG_1832 | night | right | 0 | 0.955 | 0.998 | 0.99 | 1 | False |
| IMG_1833 | night | left | 0 | 0.292 | 0.907 | 0.108 | 0 | True |
| IMG_1833 | night | right | 0 | 0.999 | 1.0 | 0.999 | 1 | False |
| IMG_1834 | night | left | 0 | 0.012 | 0.343 | 0.543 | 0 | True |
| IMG_1834 | night | right | 0 | 0.95 | 0.979 | 0.957 | 1 | False |
| IMG_1835 | night | left | 0 | 0.997 | 0.999 | 1.0 | 1 | False |
| IMG_1835 | night | right | 0 | 0.987 | 1.0 | 1.0 | 1 | False |
| IMG_1836 | night | left | 1 | 0.993 | 0.999 | 0.995 | 1 | True |
| IMG_1836 | night | right | 0 | 1.0 | 1.0 | 1.0 | 1 | False |
| IMG_1837 | night | left | 0 | 0.483 | 0.992 | 0.028 | 1 | False |
| IMG_1837 | night | right | 1 | 0.906 | 0.996 | 0.967 | 1 | True |
| IMG_1838 | night | left | 1 | 0.272 | 0.945 | 0.302 | 0 | False |
| IMG_1838 | night | right | 0 | 0.735 | 0.842 | 0.821 | 1 | False |
| IMG_1839 | night | left | 0 | 0.134 | 0.336 | 0.128 | 0 | True |
| IMG_1839 | night | right | 1 | 0.954 | 0.999 | 0.778 | 1 | True |
| IMG_1840 | night | left | 1 | 0.456 | 0.998 | 0.829 | 1 | True |
| IMG_1840 | night | right | 0 | 0.028 | 0.505 | 0.179 | 0 | True |
| IMG_1841 | night | left | 0 | 0.012 | 0.185 | 0.015 | 0 | True |
| IMG_1841 | night | right | 1 | 0.9 | 0.894 | 0.514 | 1 | True |
| IMG_1842 | night | left | 1 | 0.988 | 0.967 | 0.997 | 1 | True |
| IMG_1842 | night | right | 0 | 0.887 | 0.749 | 0.29 | 1 | False |
| IMG_1843 | night | left | 1 | 0.998 | 1.0 | 0.7 | 1 | True |
| IMG_1843 | night | right | 0 | 0.989 | 0.702 | 0.818 | 1 | False |
| IMG_1844 | night | left | 0 | 0.825 | 1.0 | 0.885 | 1 | False |
| IMG_1844 | night | right | 1 | 0.983 | 1.0 | 0.963 | 1 | True |
| IMG_1845 | night | left | 0 | 0.91 | 0.169 | 0.101 | 0 | True |
| IMG_1845 | night | right | 1 | 0.993 | 1.0 | 0.997 | 1 | True |
| IMG_1846 | night | left | 1 | 0.982 | 0.999 | 1.0 | 1 | True |
| IMG_1846 | night | right | 0 | 0.013 | 0.38 | 0.162 | 0 | True |
| IMG_1847 | night | left | 0 | 0.004 | 0.737 | 0.057 | 0 | True |
| IMG_1847 | night | right | 1 | 0.996 | 0.916 | 0.783 | 1 | True |
| IMG_1848 | night | left | 0 | 0.007 | 0.373 | 0.021 | 0 | True |
| IMG_1848 | night | right | 1 | 0.99 | 0.991 | 0.958 | 1 | True |
| IMG_1849 | night | left | 1 | 0.985 | 0.974 | 0.912 | 1 | True |
| IMG_1849 | night | right | 0 | 0.041 | 0.5 | 0.045 | 0 | True |
| IMG_1850 | night | left | 1 | 0.898 | 0.999 | 0.995 | 1 | True |
| IMG_1850 | night | right | 0 | 0.117 | 0.73 | 0.057 | 0 | True |
| IMG_1851 | night | left | 0 | 0.006 | 0.215 | 0.004 | 0 | True |
| IMG_1851 | night | right | 1 | 0.982 | 0.989 | 0.936 | 1 | True |
| IMG_1853 | night | left | 1 | 0.997 | 1.0 | 1.0 | 1 | True |
| IMG_1853 | night | right | 1 | 0.803 | 0.884 | 0.866 | 1 | True |
| IMG_1854 | night | left | 1 | 0.999 | 0.997 | 0.996 | 1 | True |
| IMG_1854 | night | right | 1 | 0.995 | 1.0 | 0.999 | 1 | True |
| IMG_1855 | night | left | 1 | 0.989 | 1.0 | 0.927 | 1 | True |
| IMG_1855 | night | right | 1 | 0.128 | 0.147 | 0.403 | 0 | False |
| IMG_1856 | night | left | 1 | 0.971 | 1.0 | 0.987 | 1 | True |
| IMG_1856 | night | right | 1 | 0.997 | 0.999 | 0.931 | 1 | True |
| IMG_1857 | night | left | 1 | 0.852 | 0.99 | 0.855 | 1 | True |
| IMG_1857 | night | right | 1 | 0.993 | 1.0 | 0.905 | 1 | True |
| IMG_1858 | night | left | 1 | 0.165 | 0.978 | 0.153 | 0 | False |
| IMG_1858 | night | right | 1 | 0.868 | 0.805 | 0.736 | 1 | True |
| IMG_1859 | night | left | 1 | 0.929 | 0.988 | 0.987 | 1 | True |
| IMG_1859 | night | right | 1 | 0.053 | 0.818 | 0.638 | 1 | True |
| IMG_1860 | night | left | 1 | 0.931 | 0.998 | 0.989 | 1 | True |
| IMG_1860 | night | right | 1 | 0.117 | 0.85 | 0.003 | 0 | False |
| IMG_1861 | night | left | 1 | 0.064 | 0.454 | 0.073 | 0 | False |
| IMG_1861 | night | right | 1 | 0.002 | 0.35 | 0.003 | 0 | False |
| IMG_1862 | night | left | 1 | 0.24 | 0.939 | 0.604 | 1 | True |
| IMG_1862 | night | right | 1 | 0.732 | 0.994 | 0.988 | 1 | True |
| IMG_1863 | night | left | 1 | 0.727 | 0.994 | 0.982 | 1 | True |
| IMG_1863 | night | right | 1 | 0.993 | 0.999 | 0.998 | 1 | True |
| IMG_1864 | night | left | 1 | 0.915 | 1.0 | 0.929 | 1 | True |
| IMG_1864 | night | right | 1 | 0.999 | 0.999 | 0.999 | 1 | True |

## 2. Plate reading in bays called occupied (YOLO11n final seed 42)

`bay` = read from the bay area (the product loop); `photo` = read from the whole photo (comparison). `plate_width` = plate width as a share of the bay width.

| photo | light | bay | truth | pred | true_plate | bay_read | bay_decision | bay_conf | plate_width | bay_outcome | photo_read | photo_outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IMG_1823 | night | left | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1824 | night | left | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1825 | night | left | 0 | 1 |  | Dubai 527 | NEEDS_REVIEW (plate_too_small) | 0.23 | 0.04 | empty_bay_review | None  | empty_bay_review |
| IMG_1825 | night | right | 0 | 1 |  | Dubai  | NEEDS_REVIEW (plate_too_small) | 0.46 | 0.07 | empty_bay_review | None  | empty_bay_review |
| IMG_1827 | night | right | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1828 | night | right | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1831 | night | left | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1831 | night | right | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1832 | night | left | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1832 | night | right | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1833 | night | right | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1834 | night | right | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1835 | night | left | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1835 | night | right | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1836 | night | left | 1 | 1 | Dubai S74426 | Dubai S74426 | READ | 0.51 | 0.23 | correct | Dubai 7426 | review |
| IMG_1836 | night | right | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1837 | night | left | 0 | 1 |  | Dubai  | NEEDS_REVIEW (plate_too_small) | 0.25 | 0.05 | empty_bay_review | none | empty_bay_review |
| IMG_1837 | night | right | 1 | 1 | Dubai Z24837 | Dubai 224837 | NEEDS_REVIEW (missing_code) | 0.27 | 0.14 | review | Dubai 232 | review |
| IMG_1838 | night | right | 0 | 1 |  | Dubai 69 | NEEDS_REVIEW (plate_too_small) | 0.22 | 0.07 | empty_bay_review | None  | empty_bay_review |
| IMG_1839 | night | right | 1 | 1 | Dubai F47710 | Dubai F47710 | READ | 0.52 | 0.23 | correct | Dubai F4710 | misread |
| IMG_1840 | night | left | 1 | 1 | Dubai V88167 | Dubai V88167 | READ | 0.91 | 0.27 | correct | Dubai N68167 | misread |
| IMG_1841 | night | right | 1 | 1 | Dubai DD53816 | Dubai DD53816 | READ | 0.41 | 0.17 | correct | Dubai 5356 | review |
| IMG_1842 | night | left | 1 | 1 | Dubai W48556 | Dubai W48556 | READ | 0.82 | 0.26 | correct | None 48555 | review |
| IMG_1842 | night | right | 0 | 1 |  | Dubai 68 | NEEDS_REVIEW (plate_too_small) | 0.27 | 0.06 | empty_bay_review | None  | empty_bay_review |
| IMG_1843 | night | left | 1 | 1 | Dubai Z91051 | Dubai 291051 | NEEDS_REVIEW (missing_code) | 0.39 | 0.13 | review | Dubai 516 | review |
| IMG_1843 | night | right | 0 | 1 |  | none | NEEDS_REVIEW |  |  | empty_bay_review | none | empty_bay_review |
| IMG_1844 | night | left | 0 | 1 |  | Dubai 7 | NEEDS_REVIEW (plate_too_small) | 0.21 | 0.07 | empty_bay_review | None  | empty_bay_review |
| IMG_1844 | night | right | 1 | 1 | Dubai L17949 | Dubai L17949 | READ | 0.8 | 0.27 | correct | Dubai 1799 | review |
| IMG_1845 | night | right | 1 | 1 | Abu Dhabi 1032803 | Abu Dhabi 10032803 | NEEDS_REVIEW (invalid_length) | 0.27 | 0.17 | review | None 328 | review |
| IMG_1846 | night | left | 1 | 1 | Dubai A58852 | Dubai 58852 | NEEDS_REVIEW (missing_code) | 0.89 | 0.28 | review | Dubai W5852 | misread |
| IMG_1847 | night | right | 1 | 1 | Dubai W48252 | Dubai W48252 | READ | 0.65 | 0.21 | correct | Dubai P4632 | misread |
| IMG_1848 | night | right | 1 | 1 | Sharjah 74207 | Sharjah 74207 | READ | 0.67 | 0.26 | correct | Dubai 74207 | review |
| IMG_1849 | night | left | 1 | 1 | Dubai M17267 | Dubai M17267 | READ | 0.65 | 0.17 | correct | Dubai 17267 | review |
| IMG_1850 | night | left | 1 | 1 | Dubai D81929 | Dubai D81929 | READ | 0.47 | 0.23 | correct | Dubai 8629 | review |
| IMG_1851 | night | right | 1 | 1 | Dubai GG28075 | Dubai G28075 | READ | 0.39 | 0.25 | misread | Dubai 2906 | review |
| IMG_1853 | night | left | 1 | 1 | Sharjah 593105 | None 3593105 | NEEDS_REVIEW (no_emirate) | 0.3 | 0.26 | review | Sharjah S3315 | misread |
| IMG_1853 | night | right | 1 | 1 | Dubai I26590 | Dubai 26590 | NEEDS_REVIEW (missing_code) | 0.88 | 0.14 | review | None 22687 | review |
| IMG_1854 | night | left | 1 | 1 | Dubai GG28075 | Dubai G28075 | READ | 0.74 | 0.26 | misread | Dubai W2403 | misread |
| IMG_1854 | night | right | 1 | 1 | Dubai R66918 | Dubai R66918 | READ | 0.54 | 0.26 | correct | Dubai H96916 | misread |
| IMG_1855 | night | left | 1 | 1 | Dubai E79928 | Dubai E79928 | READ | 0.8 | 0.26 | correct | Dubai 2899 | review |
| IMG_1856 | night | left | 1 | 1 | Dubai N81803 | Dubai N81803 | READ | 0.43 | 0.26 | correct | Dubai W80 | misread |
| IMG_1856 | night | right | 1 | 1 | Dubai P26405 | Dubai F26405 | READ | 0.6 | 0.13 | misread | None O203 | review |
| IMG_1857 | night | left | 1 | 1 | Dubai M55439 | Dubai M55439 | READ | 0.77 | 0.16 | correct | Dubai 55449 | review |
| IMG_1857 | night | right | 1 | 1 | Dubai S99566 | Dubai S99566 | READ | 0.76 | 0.29 | correct | None E99966 | review |
| IMG_1858 | night | right | 1 | 1 | Dubai B77998 | Dubai 77998 | NEEDS_REVIEW (missing_code) | 0.89 | 0.27 | review | Dubai 77698 | review |
| IMG_1859 | night | left | 1 | 1 | Dubai S1884 | Dubai S1894 | READ | 0.57 | 0.23 | misread | Dubai 184 | review |
| IMG_1859 | night | right | 1 | 1 | Dubai Y20947 | Dubai 20947 | NEEDS_REVIEW (missing_code) | 0.89 | 0.25 | review | Dubai 2047 | review |
| IMG_1860 | night | left | 1 | 1 | Dubai U94847 | Dubai U94847 | READ | 0.56 | 0.24 | correct | Dubai W9434 | misread |
| IMG_1862 | night | left | 1 | 1 | Abu Dhabi 817136 | Abu Dhabi 817136 | READ | 0.56 | 0.16 | correct | Abu Dhabi 25 | misread |
| IMG_1862 | night | right | 1 | 1 | Dubai V88167 | Dubai V88167 | READ | 0.81 | 0.24 | correct | Dubai 88167 | review |
| IMG_1863 | night | left | 1 | 1 | Dubai B35710 | Dubai P35710 | READ | 0.29 | 0.25 | misread | Dubai 3570 | review |
| IMG_1863 | night | right | 1 | 1 | Dubai GG13096 | Dubai GG13096 | READ | 0.25 | 0.22 | correct | Dubai 1995 | review |
| IMG_1864 | night | left | 1 | 1 | Dubai FF27017 | Dubai F27017 | READ | 0.26 | 0.23 | misread | Dubai 2207 | review |
| IMG_1864 | night | right | 1 | 1 | Dubai H12524 | Dubai H12524 | READ | 0.7 | 0.23 | correct | Dubai 2544 | review |

## 3. End to end

Bays fully right (occupancy right and, if occupied, the plate read right or a missing plate sent to review): 46 of 86.
