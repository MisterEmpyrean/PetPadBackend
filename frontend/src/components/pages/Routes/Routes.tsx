import React from "react";
import { Redirect } from "react-router";
import { Switch } from "react-router-dom";

import PublicRoute from "../../molecules/PublicRoute/PublicRoute";
import Profile from "../../templates/Profile";
import Homepage from "../Homepage";
import Page404 from "../Page404";
import Register from "../Register";
import { ROUTES } from "./types";

const Routes = () => (
    <Switch>
        <PublicRoute
            exact
            path={ROUTES.HOMEPAGE}
            component={Homepage}
        />
        <PublicRoute
            exact
            path={ROUTES.REGISTER}
            component={Register}
        />
        <PublicRoute
            exact
            path={ROUTES.PROFILE}
            component={Profile}
        />
        <PublicRoute exact path="/404" component={Page404} />
        <Redirect to="/404" />
    </Switch>
);

export default Routes;