-- using subquery in update
explain analyze update full_names
set
    status = (
        select
            s.status
        from short_names s
        where
            s.name = split_part(full_names.name, '.', 1)
    )
