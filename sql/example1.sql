-- using update join
explain analyze update full_names f
set
    status = s.status
from short_names s
where
    s.name = split_part(f.name, '.', 1)
