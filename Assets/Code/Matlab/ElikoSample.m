function [ComplexOut] = ElikoSample()
    while 1
        try
            [ZModule, ZPhase] = ElikoRead();
        catch 
            [ZModule, ZPhase] = ElikoRead();
        end

        ComplexOut = zeros(size(ZModule));
        for row = 1: size(ZModule, 1)
            for col = 1: size(ZModule, 2)
               mod = ZModule(row, col);
               ang = ZPhase(row, col);
               [X, Y] = pol2cart(deg2rad(ang), mod);
               ComplexOut(row, col) = complex(X, Y);
            end
        end
        % check if the electrode does not contact tissue
%         if any(any(ComplexOut<=0, 2))
%             %disp(ComplexOut)
%             disp("Discarding data, zero or negative found in real")
%             continue               
%         end
        break
    end
end