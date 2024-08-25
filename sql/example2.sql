-- using explicit join for update
explain analyze update full_names f
set
    status = sub.status
from (
    select
        fn.name,
        s.status
    from full_names fn
    join short_names s on s.name = split_part(fn.name, '.', 1)
) as sub
where
    f.name = sub.name
