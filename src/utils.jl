function linear_interp(x, xp, fp)
	d = xp[2] - xp[1]
	if x <= xp[1]
		return ((1-(xp[1]-x) / d) * fp[1]) + (((360-xp[end]-x) / d) * fp[end])
	elseif x >= xp[end]
		return ((1-(360+xp[1]-x) / d) * fp[1]) + ((1-(x-xp[end]) / d) * fp[end])
	else
		left = convert(Int, ((x-xp[1]) ÷ d) + 1)
		right = left+1
		return ((1-(x-xp[left]) / d) * fp[left]) + ((1-(xp[right]-x) / d) * fp[right])
	end
end

function numerical_diff_lognormal_cdf(step_size)
	n = LogNormal()
	F(x) = cdf(n, x)
	f(x) = pdf(n, x)
	[quadgk(x -> F(x+i) * f(x), 0, Inf)[1] for i in 0:step_size:10]
end