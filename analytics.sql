Select 
date(o.order_date) as order_day,
sum(oi.quantity * oi.item_price) as daily_revenue,
avg(sum(oi.quantity * oi.item_price)) OVER (order by date(o.order_date) rows between 6 preceding and current row) as rolling_7_day_avg_revenue
from orders o
join order_items oi on o.order_id = oi.order_id
group by date(o.order_date)
order by order_day desc;