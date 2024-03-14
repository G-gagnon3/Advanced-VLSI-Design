
lower_cutoff = 0.2;
upper_cutoff = 0.23;
tap_minimum = 100;
tap_maximum = 500;
tap_quantity = 400;

cutoff_amp = db2mag(-80);
%taps = fir1(tap_quantity, cutoff);
taps = firpm(tap_quantity, [0 lower_cutoff upper_cutoff 1], [1 1 0 0]);
%for tap_quantity = tap_minimum:tap_maximum
%    taps = cfirpm(tap_quantity,[-1 -0.23 -0.2 0.2 0.23 1],@lowpass);
%end

[h{1},w{1}] = freqz(taps,1,512);
freqz(taps,1,512);

[q_taps16, dq16] = quantize_taps(taps, 16);

[q_taps8, dq8] = quantize_taps(taps, 8);

[q_taps4, dq4] = quantize_taps(taps, 4);

dq_taps16 = q_taps16*dq16(1) + dq16(2);
dq_taps8 = q_taps8*dq8(1) + dq8(2);
dq_taps4 = q_taps4*dq4(1) + dq4(2);

[h{2},w{2}] = freqz(dq_taps16,1,512);
[h{3},w{3}] = freqz(dq_taps8,1,512);
[h{4},w{4}] = freqz(dq_taps4,1,512);


figure()
subplot(2,1,1)
for k = 1:4
    semilogy(w{k}/pi,abs(h{k}))
    hold on
end
hold off
grid
xlim([0.01 1]);
xlabel('Frequency (rad/s)');
ylabel('Attenuation (dB)');
legend('Unquantized','Quantized 16', 'Quantized 8', 'Quantized 4', 'Location',"southwest");
subplot(2,1,2)
for k = 1:4
    semilogx(w{k}/pi,angle(h{k})*180/pi)
    hold on 
end
hold off
grid
xlabel('Frequency (rad/s)');
ylabel('Phase');
legend('Unquantized','Quantized 16', 'Quantized 8', 'Quantized 4','Location',"southwest");

function [x_q, dq] = quantize_taps(x, bits)
    % Base values
    num_q_vals = 2^(bits);
    max_scale = (num_q_vals-1);

    % Statistical characteristics
    min_x = min(x);
    max_x = max(x);
    range_x = max_x-min_x;
    mean_x = mean(x);
    std_dev_x = sqrt(var(x));
    disp([min_x max_x range_x mean_x std_dev_x])

    % Do quantization
    %% Clip, Normalize, Scale
    lower_clip_bound = min_x;%mean_x; %- 4*std_dev_x;
    upper_clip_bound = max_x;%mean_x; %+ 4*std_dev_x;

    x_clipped = min(max(x, lower_clip_bound), mean_x + upper_clip_bound);
    clip_min_x = max(min_x, lower_clip_bound);
    clip_max_x = min(max_x, upper_clip_bound);
    clip_range_x = clip_max_x - clip_min_x;

    x_norm = (x_clipped - clip_min_x)/(clip_range_x); % Make sure min_x is adjusted to reflect min after clipping
    adjusted_range = x_norm*max_scale;
    % Round to get the effective value
    x_q = round(adjusted_range);

    % Get the dequantize values
    %% ax + b
    a = clip_range_x/max_scale;
    b = clip_min_x;
    dq = [a b];

end