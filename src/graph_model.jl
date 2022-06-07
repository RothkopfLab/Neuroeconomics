const _abs_angle_xps = (30, 90, 150, 210, 270, 330)

function construct_all_features(df)
	features = zeros((size(df, 1), 6))
	# amplitude
	features[:, 1] = df.ampChosen ./ 412
	features[:, 4] = df.ampNotChosen ./ 412
	# absolute angle
	features[:, 2] = df.angleAbsoluteChosen
	features[:, 5] = df.angleAbsoluteNotChosen
	# relative angle
	features[:, 3] = abs.(df.angleChosen .- 180) ./ 180
	features[:, 6] = abs.(df.angleNotChosen .- 180) ./ 180
	features
end

find_approx_idx(v) = round(Int, min((abs(v) / 0.001) + 1, 10000))

@model function all_features_lognormal(features, decisions, cdf_diff_lognormal)
	# sample weights for the features
	w_amp ~ Normal(0, 5)
	w_dir ~ MvNormal(5, 5) # this is a 5D zero-mean isotropic normal with σ=5
	w_cid ~ Normal(0, 5)
	
	N = size(features, 1)
	# iterate over all decisions
	for i in 1:N
		# calculate the value for both targets and the respective difference
		v1 = features[i, 1] * w_amp +
			linear_interp(features[i, 2], _abs_angle_xps, [1, w_dir...]) +
			features[i, 3] * w_cid
		v2 = features[i, 4] * w_amp +
			linear_interp(features[i, 5], _abs_angle_xps, [1, w_dir...]) +
			features[i, 6] * w_cid
		value_diff = v1 - v2

		# calculate the probability for the chosen target
		approx_idx = find_approx_idx(value_diff)
		prob = cdf_diff_lognormal[approx_idx]
		prob = value_diff >= 0 ? prob : 1 - prob
		decisions[i] ~ Bernoulli(prob)
	end
end

function sample_single_subj_chain_lognormal(decisions, subj_id)
	cdf_diff_lognormal = numerical_diff_lognormal_cdf(0.001)
	subj_features = construct_all_features(decisions[decisions.partName .== subj_id, :])
	subj_decs = ones(size(subj_features, 1))
	subj_model = all_features_lognormal(subj_features, subj_decs, cdf_diff_lognormal)
	sample(subj_model, HMC(0.01, 10), 1000, progress=true)
end
